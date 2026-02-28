import streamlit as st
import hashlib, re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

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

st.title("🔓 步驟四：Bob 解密訊息")
db = st.number_input("輸入 Bob 私鑰 (dB):", value=987654321)
qa_input = st.text_input("請貼上 Alice 的公鑰資料 (x, y):", placeholder="0x..., 0x...")
package_hex = st.text_area("請貼上密文包 (Hex):")

if st.button("執行解密"):
    try:
        parts = qa_input.split(',')
        coords = [re.sub(r'[^0-9a-f]', '', s.lower()) for s in parts]
        QA = (int(coords[0], 16), int(coords[1], 16))
        
        S = ec_mul(db, QA)
        shared_key = hashlib.sha256(str(int(S[0])).encode()).digest()
        
        cp = re.sub(r'[^0-9a-f]', '', package_hex.lower())
        raw_data = bytes.fromhex(cp)
        iv, ct = raw_data[:16], raw_data[16:]
        
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        original = unpad(cipher.decrypt(ct), 16).decode('utf-8')
        
        st.balloons()
        st.success(f"🔓 解密成功！還原訊息：{original}")
        st.write(f"🧬 驗證共同點 Sx: {hex(S[0])}")
    except Exception as e:
        st.error(f"❌ 錯誤：{str(e)}")
