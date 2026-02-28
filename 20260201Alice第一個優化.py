P = 6277101735386680763835789423207666416102355444464034512897
A, B = 1, 14
G = (0x9780a221f584e62552f9f878f5a133240e53a39e832623b0, 
     0x2401f7027b40939527ec56133299719364407f38072e9f06)

def inv(n, q):
    return pow(n, q - 2, q)

def ec_add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1, x2, y2 = P1[0], P1[1], P2[0], P2[1]
    
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None  # 互為相反點，結果為無窮遠點
        # 點加倍公式
        m = (3 * x1 * x1 + A) * inv(2 * y1, P) % P
    else:
        # 點相加公式
        m = (y2 - y1) * inv(x2 - x1, P) % P
        
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    return (x3, y3)

def ec_mul(k, P1):
    res = None
    temp = P1
    while k > 0:
        if k % 2 == 1:
            res = ec_add(res, temp)
        temp = ec_add(temp, temp)
        k //= 2
    return res

dA = int(input("🔑 Alice，請輸入你的私鑰 dA: "))
QA = ec_mul(dA, G)
print(f"\n✅ 你的公鑰 QA 為：\nX: {hex(QA[0])}\nY: {hex(QA[1])}")
