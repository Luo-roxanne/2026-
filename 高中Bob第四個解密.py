import streamlit as st
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- 核心參數與函數 ---
P = 6277101735386680763835789423207666416102355444464034512897
A = 1

def inv(n, q):
    return pow(n, q - 2, q)

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
    res = None
    temp = P1
    while k > 0:
        if k % 2 == 1: res = ec_add(res, temp)
        temp = ec_add(temp, temp)
        k //= 2
    return res

# --- 介面設計 ---
st.title("🔓 程式四：Bob 訊息解密端 (修正版)")
st.markdown("請確保輸入的公鑰與 Alice 端完全一致。")

# 輸入區
db = st.number_input("1. 輸入 Bob 的私鑰 (dB):", value=987654321)
qa_x_input = st.text_input("2. 輸入 Alice 的公鑰 X (需含 0x):", placeholder="0x...")
qa_y_input = st.text_input("3. 輸入 Alice 的公鑰 Y (需含 0x):", placeholder="0x...")
package_input = st.text_area("4. 貼上收到的密文包 (Hex 字串):", placeholder="在此貼上長串十六進位數字...")

if st.button("執行解密"):
    if not (qa_x_input and qa_y_input and package_input):
        st.error("❌ 請填寫完整公鑰與密文包資訊！")
    else:
        try:
            # 1. 處理輸入格式 (去除空格並轉為整數)
            qa_x = int(qa_x_input.strip(), 16)
            qa_y = int(qa_y_input.strip(), 16)
            QA = (qa_x, qa_y)
            
            # 2. 計算共同金鑰 S = db * QA
            S = ec_mul(db, QA)
            if S is None:
                st.error("❌ 計算出的共同點為無窮遠點，請檢查公鑰是否有誤。")
            else:
                # 3. 衍生 AES Key (與 Alice 端必須完全相同)
                # 使用 S[0] 的字串進行 SHA256
                shared_key = hashlib.sha256(str(S[0]).encode()).digest()
                
                # 4. 解析密文包 (前 16 bytes 是 IV，後面是密文)
                raw_data = bytes.fromhex(package_input.strip())
                if len(raw_data) < 16:
                    st.error("❌ 密文包長度不足（需包含 16 位 IV）。")
                else:
                    iv_rec = raw_data[:16]
                    ct_rec = raw_data[16:]
                    
                    # 5. AES 解密
                    cipher = AES.new(shared_key, AES.MODE_CBC, iv_rec)
                    decrypted_data = cipher.decrypt(ct_rec)
                    
                    # 6. 去除填充 (Unpad) 並轉碼
                    original_msg = unpad(decrypted_data, 16).decode('utf-8')
                    
                    st.balloons()
                    st.success(f"🎊 解密成功！")
                    st.subheader(f"還原訊息：{original_msg}")
                    st.write(f"🔐 驗證共同金鑰 Sx: {hex(S[0])}")
                    
        except Exception as e:
            st.error(f"❌ 解密失敗！錯誤原因：{str(e)}")
            st.info("💡 小撇步：請確認密文包是否完整複製，且私鑰與公鑰是否正確。")
