// frontend/src/components/auth/Login/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5002/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        alert('Login successful');
        navigate('/home'); // 使用 React Router 导航
      } else {
        alert(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while trying to log in');
    }
  };

  return (
    <>
      <div className="header" onClick={() => navigate('/')}>
        <span className="black-text">Book</span>
        <span className="green-text">worm</span>
      </div>

      <div className="container">
        <h1>Log in</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
            />
          </div>

          <div className="form-group">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </div>

          <button type="submit" className="login-btn">
            Log In
          </button>
        </form>
        <div className="alt">
          <span className="black-text">Don't have an account?</span>
          <span className="green-text" onClick={() => navigate('/signup')}>
            Sign Up
          </span>
        </div>
      </div>
    </>
  );
}

export default Login;