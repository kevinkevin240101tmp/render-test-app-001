from flask import Flask, render_template, request, redirect, session
import os
import openai

app = Flask(__name__)
app.secret_key = "換成你自己的安全字串"  # session 必須

# 登入帳號密碼（小型家用測試）
USERS = {
    "kevin": "1234",
    "didi": "abcd"
}

# 讀取 OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


# 登入頁面
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect("/")
        else:
            message = "❌ 帳號或密碼錯誤"
    return render_template("login.html", message=message)


# 登出功能
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# 主頁生成貼文
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")  # 未登入 → 導到登入頁

    message = ""
    posts = ""
    
    if request.method == "POST":
        brand = request.form.get("brand")
        product = request.form.get("product")
        audience = request.form.get("audience")
        
        if not openai.api_key:
            message = "❌ API Key 尚未設定"
        else:
            try:
                prompt = f"""
                請幫我為品牌「{brand}」的產品「{product}」生成 5 則貼文，
                目標客群是「{audience}」。
                請每則貼文都簡短、活潑、有吸引力。
                """
                response = openai.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": prompt}],
                )
                posts = response.choices[0].message.content

            except Exception as e:
                message = f"❌ 發生錯誤：{str(e)}"
    
    return render_template("index.html", message=message, posts=posts)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
