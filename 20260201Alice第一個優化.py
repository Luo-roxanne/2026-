import streamlit as st

# NIST P-192 參數
P = 6277101735386680763835789423207666416102355444464034512897
A = 1
G = (0x9780a221f584e62552f9f878f5a133240e53a39e832623b0, 
     0x2401f7027b40939527ec56133299719364407f38072e9f06)

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

st.title("👤 步驟一：Alice 生成公鑰")
da = st.number_input("【Alice】請輸入您的私鑰 (dA):", value=123456789)

if st.button("產生公鑰資料"):
    QA = ec_mul(da, G)
    st.success("成功！請將下方整行文字複製並傳給 Bob：")
    # 格式化為一鍵複製的字串
    pub_string = f"{hex(QA[0])}, {hex(QA[1])}"
    st.code(pub_string)
