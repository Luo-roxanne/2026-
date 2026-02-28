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

st.title("🔓 Bob 訊息解密端")
db = st.number_input("輸入 Bob 私鑰:", value=987654321)
qa_x = st.text_input("輸入 Alice 公鑰 X (0x...):")
qa_y = st.text_input("輸入 Alice 公鑰 Y (0x...):")
package_hex = st.text_area("貼上收到的密文包 (Hex):")

if st.button("執行解密"):
    try:
        QA = (int(qa_x, 16), int(qa_y, 16))
        S = ec_mul(db, QA)
        shared_key = hashlib.sha256(str(S[0]).encode()).digest()
        
        data = bytes.fromhex(package_hex)
        iv, ct = data[:16], data[16:]
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        original = unpad(cipher.decrypt(ct), 16).decode()
        
        st.success(f"🔓 解密成功！原始訊息：{original}")
        st.write(f"✅ 驗證共同點 Sx: {hex(S[0])}")
    except:
        st.error("解密失敗，請檢查金鑰或密文。")