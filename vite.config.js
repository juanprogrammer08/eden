import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuración de Vite para el proyecto React 18
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy para redirigir llamadas a la API al backend FastAPI
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
  resolve: {
    alias: {
      // Alias para facilitar importaciones si se requiere
      '@': '/src',
    },
  },
})