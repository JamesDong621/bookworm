import React, { useState, useEffect } from 'react';

function App() {
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (userData && userData.name) {
      setUserName(userData.name);
    }
  }, []);

  return (
    <div>
      <h1>Welcome back, {userName}</h1>
      {/* other components */}
    </div>
  );
}

export default App; 