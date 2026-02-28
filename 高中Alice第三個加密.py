import streamlit as st
import hashlib, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

P = 6277101735386680763835789423207666416102355444464034512897
A = 1
G = (0x9780a221f584e62552f9f878f5a133240e53a39e832623b0, 
     0x2401f7027b40939527ec56133299719364407f38072e9f06)

def inv(n, q): return pow(n, q - 2, q)
def ec_add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1, x2, y2 = P1[0], P1[1], P2[0], P2[1]
    if x1 == x2:
        if (y1 + y2) % P == 0: return None
        m = (3 * x1 * x1 + A) * inv(2 * y1, P) % P
    else:
        m = (y2 - y1) * inv(x2 - x1, P) % P
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def ec_mul(k, P1):
    res, temp = None, P1
    while k > 0:
        if k % 2 == 1: res = ec_add(res, temp)
        temp = ec_add(temp, temp)
        k //= 2
    return res

st.title("🔒 Alice 訊息加密端")
da = st.number_input("輸入 Alice 私鑰:", value=123456789)
qb_x = st.text_input("輸入 Bob 公鑰 X (0x...):")
qb_y = st.text_input("輸入 Bob 公鑰 Y (0x...):")
msg = st.text_area("要傳送的秘密訊息/網址:")

if st.button("執行加密"):
    if qb_x and qb_y:
        QB = (int(qb_x, 16), int(qb_y, 16))
        S = ec_mul(da, QB)
        shared_key = hashlib.sha256(str(S[0]).encode()).digest()
        iv = os.urandom(16)
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(msg.encode(), 16))
        
        st.write(f"✅ 協商共同點 Sx: {hex(S[0])}")
        st.warning(f"📦 請複製以下密文包傳給 Bob:\n{(iv + ciphertext).hex()}")