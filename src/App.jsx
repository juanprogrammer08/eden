import React, { useState, useEffect } from 'react'

// Componente para mostrar un formulario de login o registro
function AuthForm({ mode, onAuthSuccess }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  // Enviar datos al endpoint correspondiente (login o register)
  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)
      const res = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString()
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Error en autenticación')
      }
      const data = await res.json()
      // Guardar token JWT en localStorage
      localStorage.setItem('token', data.access_token)
      onAuthSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-form">
      <h2>{mode === 'login' ? 'Iniciar sesión' : 'Registrarse'}</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Usuario
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
            autoComplete="username"
            disabled={loading}
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            disabled={loading}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Procesando...' : mode === 'login' ? 'Entrar' : 'Registrar'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  )
}

// Componente para proteger rutas que requieren autenticación
function PrivateRoute({ children, onLogout }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Obtener datos del usuario autenticado
  useEffect(() => {
    async function fetchUser() {
      setLoading(true)
      setError(null)
      const token = localStorage.getItem('token')
      if (!token) {
        setLoading(false)
        setUser(null)
        return
      }
      try {
        const res = await fetch('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!res.ok) {
          throw new Error('No autorizado')
        }
        const data = await res.json()
        setUser(data)
      } catch (err) {
        setError(err.message)
        setUser(null)
        localStorage.removeItem('token')
      } finally {
        setLoading(false)
      }
    }
    fetchUser()
  }, [])

  // Mostrar estado mientras se carga o error
  if (loading) return <p>Cargando...</p>
  if (error) return (
    <div>
      <p>Error: {error}</p>
      <button onClick={() => {
        localStorage.removeItem('token')
        onLogout()
      }}>Volver a autenticar</button>
    </div>
  )
  if (!user) return <p>No autorizado. Por favor, inicie sesión.</p>

  // Renderizar contenido protegido
  return children(user)
}

// Componente principal de la aplicación
export default function App() {
  const [mode, setMode] = useState('login') // 'login' o 'register'
  const [authenticated, setAuthenticated] = useState(false)

  // Comprobar si hay token en localStorage para estado inicial
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) setAuthenticated(true)
  }, [])

  // Manejar cierre de sesión
  function handleLogout() {
    localStorage.removeItem('token')
    setAuthenticated(false)
    setMode('login')
  }

  // Cambiar entre login y registro
  function toggleMode() {
    setMode(mode === 'login' ? 'register' : 'login')
  }

  // Renderizado condicional según autenticación
  if (!authenticated) {
    return (
      <div className="container">
        <AuthForm
          mode={mode}
          onAuthSuccess={() => setAuthenticated(true)}
        />
        <p>
          {mode === 'login' ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}{' '}
          <button onClick={toggleMode} className="link-button">
            {mode === 'login' ? 'Regístrate' : 'Inicia sesión'}
          </button>
        </p>
      </div>
    )
  }

  // Contenido protegido tras login
  return (
    <div className="container">
      <header>
        <h1>Bienvenido a YERUZZA STUDIO</h1>
        <button onClick={handleLogout}>Cerrar sesión</button>
      </header>
      <main>
        <PrivateRoute onLogout={handleLogout}>
          {(user) => (
            <div>
              <p>Usuario: <strong>{user.username}</strong></p>
              <p>Esta es la zona protegida de la aplicación.</p>
              {/* Aquí se pueden agregar rutas y componentes protegidos */}
            </div>
          )}
        </PrivateRoute>
      </main>
    </div>
  )
}