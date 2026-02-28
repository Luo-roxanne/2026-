import streamlit as st
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- 核心參數與函數 (確保與 Alice 完全相同) ---
P = 6277101735386680763835789423207666416102355444464034512897
A = 1

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

st.title("🔓 Bob 最終修正版：解密端")

db = st.number_input("1. 輸入 Bob 私鑰 (dB):", value=987654321)
qa_x_str = st.text_input("2. 輸入 Alice 公鑰 X:")
qa_y_str = st.text_input("3. 輸入 Alice 公鑰 Y:")
package_hex = st.text_area("4. 貼上密文包 (Hex):")

if st.button("執行解密"):
    try:
        # 清理並轉換輸入
        xa = int(qa_x_str.strip(), 16)
        ya = int(qa_y_str.strip(), 16)
        QA = (xa, ya)
        
        # 1. 計算共同金鑰
        S = ec_mul(db, QA)
        
        # 2. 衍生 AES 金鑰 (這一步必須與 Alice 的加密程式完全死鎖一致)
        # 建議統一：將 S[0] 轉為整數後轉成 bytes
        shared_key = hashlib.sha256(str(int(S[0])).encode()).digest()
        
        # 3. 處理密文包 (去除可能存在的空格或 0x)
        clean_package = package_hex.strip().lower().replace("0x", "").replace(" ", "").replace("\n", "")
        raw_data = bytes.fromhex(clean_package)
        
        iv = raw_data[:16]
        ciphertext = raw_data[16:]
        
        # 4. AES 解密
        cipher = AES.new(shared_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # 5. Unpad
        original_msg = unpad(decrypted, 16).decode('utf-8')
        
        st.success(f"🔓 解密成功！還原訊息：{original_msg}")
        st.write(f"🧬 共同金鑰校準值 Sx: {hex(S[0])}")

    except ValueError as e:
        st.error(f"❌ 格式錯誤：請確保輸入的是正確的十六進位數字。")
    except Exception as e:
        st.error(f"❌ 解密失敗：{str(e)}")
        st.info("💡 提示：通常是因為私鑰輸入錯誤，導致生成的共同金鑰與加密端不符，請檢查 Alice 端顯示的 Sx 是否與此處一致。")
