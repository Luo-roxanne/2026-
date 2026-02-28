import streamlit as st
import hashlib, os, re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

P, A = 0xfffffffffffffffffffffffffffffffeffffffffffffffff, 1

def inv(n, q): return pow(n, q - 2, q)
def ec_add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1, x2, y2 = P1[0] % P, P1[1] % P, P2[0] % P, P2[1] % P
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

st.title("🔒 步驟三：Alice 加密訊息")
da = st.number_input("輸入 Alice 私鑰 (dA):", value=123456789)
qb_input = st.text_input("請貼上 Bob 的公鑰資料 (x, y):", placeholder="0x..., 0x...")
msg = st.text_area("請輸入要加密的訊息:")

if st.button("執行加密"):
    try:
        # 清理並拆解輸入
        parts = qb_input.split(',')
        coords = [re.sub(r'[^0-9a-f]', '', s.lower()) for s in parts]
        QB = (int(coords[0], 16), int(coords[1], 16))
        
        S = ec_mul(da, QB)
        # 使用整數轉型確保兩端雜湊基礎一致
        shared_key = hashlib.sha256(str(int(S[0])).encode()).digest()
        
        iv = os.urandom(16)
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(msg.encode('utf-8'), 16))
        
        st.success(f"共同點 Sx: {hex(S[0])}")
        st.warning(f"📦 請將密文包傳給 Bob:\n{(iv + ciphertext).hex()}")
    except Exception as e:
        st.error(f"錯誤：請檢查輸入格式 ({e})")
