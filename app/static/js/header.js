function createHeader() {
  // 創建一個 header 物件
  var headerObj = document.createElement('header');
  headerObj.classList.add('desktop');

  // 設置 header 的內容
  headerObj.innerHTML = `
      <div class="navigation">
        <a href="/" class="left">
          <span class="title">台北一日遊</span>
        </a>
        <div class="right">
          <a href="#" class="menu-item" onclick="openBooking()">預定行程</a>
          <a href="#" class="menu-item" onclick="openPopup('signin')">登入/註冊</a>
        </div>
      </div>

      <div class="signup-overlay">
        <div class="popup-bar"></div>
        <div class="signup">
          <button class="close" onclick="closePopup('signup')"></button>
          <div class="pop-bar"></div>
          <div class="pop-group">
            <h3>註冊會員帳號</h3>
            <input type="text" placeholder="輸入姓名"><br>
            <input type="text" placeholder="輸入電子郵件"><br>
            <input type="password" placeholder="輸入密碼"><br>
            <button class="signup-btn" onclick="signup()">註冊新帳戶</button><br>
            <p>已經有帳戶了?<a href="#" onclick="closePopup('signup'); openPopup('signin');">點此登入</a></p>
          </div>
        </div>
      </div>

      <div class="signin-overlay">
        <div class="popup-bar"></div>
        <div class="signin">
          <button class="close" onclick="closePopup('signin')"></button>
          <div class="pop-bar"></div>
          <div class="pop-group">
            <h3>登入會員帳號</h3>
            <input type="text" placeholder="輸入電子郵件"><br>
            <input type="password" placeholder="輸入密碼"><br>
            <button class="signin-btn" onclick="signin()">登入帳戶</button><br>
            <p>還沒有帳戶?<a href="#" onclick="closePopup('signin'); openPopup('signup');">點此註冊</a></p>
          </div>
        </div>
      </div>
    `;

  // 尋找現有的 header 標籤
  var existingHeader = document.querySelector('header');

  // 插入 headerObj 到現有的 header 標籤中
  existingHeader.innerHTML = headerObj.innerHTML;

  checkUserLoggedIn();
}

function checkUserLoggedIn() {
  if (localStorage.getItem('token')) {
    // 如果有數值，將第二個 <a> 元素改為「登出系統」
    var logoutLink = document.createElement('a');
    logoutLink.href = '#';
    logoutLink.classList.add('menu-item');
    logoutLink.textContent = '登出系統';
    logoutLink.onclick = function () {
      // 清除 localStorage
      localStorage.removeItem('token');
      // 重新載入頁面
      location.reload();
    };

    // 將原始的第二個 <a> 元素替換為「登出系統」的連結
    var originalLink = document.querySelector('.navigation .right a:nth-child(2)');
    originalLink.parentNode.replaceChild(logoutLink, originalLink);
  }
}

function openPopup(kind) {
  const overlay = document.getElementsByClassName(kind + "-overlay")[0];
  overlay.style.display = 'flex';
}

function closePopup(kind) {
  const overlay = document.getElementsByClassName(kind + "-overlay")[0];
  overlay.style.display = 'none';
  checkUserLoggedIn();
}

const signin = () => {
  const emailInput = document.querySelector('.signin .pop-group input[type="text"]');
  const passwordInput = document.querySelector('.signin .pop-group input[type="password"]');
  const resultParagraph = document.querySelector('.signin .pop-group p');
  fetch('/api/signin', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: emailInput.value,
      password: passwordInput.value
    })
  })
    .then(response => response.json())
    .then(data => {
      // 在這裡處理API的回應
      resultParagraph.textContent = data.result;
      localStorage.setItem('token', data.token);
    })
    .catch(error => {
      // 在這裡處理錯誤
      console.error(error);
    });
};

const signup = () => {
  const nameInput = document.querySelector('.signup .pop-group input[type="text"]:nth-of-type(1)');
  const emailInput = document.querySelector('.signup .pop-group input[type="text"]:nth-of-type(2)');
  const passwordInput = document.querySelector('.signup .pop-group input[type="password"]');
  const resultParagraph = document.querySelector('.signup .pop-group p');

  fetch('/api/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: nameInput.value,
      email: emailInput.value,
      password: passwordInput.value
    })
  })
    .then(response => response.json())
    .then(data => {
      // 在這裡處理API的回應
      resultParagraph.textContent = data.result;
    })
    .catch(error => {
      // 在這裡處理錯誤
      console.error(error);
    });
};

const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch('/api/currentuser', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        .then(response => response.json())
        .then(data => {
          resolve(data);
        })
        .catch(error => {
          console.error(error);
          reject(error);
        });
    } else {
      resolve(false);
    }
  });
};
    
const getOrder = () => {
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch('/api/get_order', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        .then(response => response.json())
        .then(data => {
          resolve(data);
        })
        .catch(error => {
          console.error(error);
          reject(error);
        });
    } else {
      resolve(false);
    }
  });
};
    
const deleteOrder = () => {
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch('/api/delete_order', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        .then(response => response.json())
        .then(data => {
          resolve(data);
          location.reload();
        })
        .catch(error => {
          console.error(error);
          reject(error);
        });
    } else {
      resolve(false);
    }
  });
};

function openBooking() {
  // 如果 getCurrentUser() 回傳true，導向到/booking，若無則 openPopup("signin")
  getCurrentUser()
  .then(result => {
    if (result.email) {
      window.location.href = "/booking"; // Redirect to /booking if result is true
    } else {
      openPopup("signin");
    }
  })
  .catch(error => {
    console.log(error);
  });
} 
