// frontend/src/pages/FirstPage/FirstPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './FirstPage.css';
import mascotImage from '../../assets/furfur.png'; // 需要将图片移动到 assets 目录

function FirstPage() {
  const navigate = useNavigate();

  return (
    <div>
      <div className="header">
        <span className="black-text">Book</span>
        <span className="green-text">worm</span>
      </div>
      
      <div id="slogan">
        <p>Make reading simple, and learning endless!</p>
      </div>

      <img src={mascotImage} alt="furfur" className="mascot" />
      
      <div className="signup-btn" onClick={() => navigate('/signup')}>
        Sign Up
      </div>

      <div className="login-btn" onClick={() => navigate('/login')}>
        Login
      </div>
    </div>
  );
}

export default FirstPage;