from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- 初期設定 ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'itta_super_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- データベースモデル ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- HTMLテンプレート（丸みのあるフォントと青系パステルカラーに変更） ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>itta - 創作の願望を呟くSNS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'M PLUS Rounded 1c', sans-serif; }
    </style>
</head>
<body class="bg-sky-50 text-gray-700 flex flex-col min-h-screen">
    
    <nav class="bg-white/80 backdrop-blur shadow-sm border-b border-sky-100 p-4 flex justify-between items-center sticky top-0 z-50">
        <a href="{{ url_for('index') }}" class="text-3xl font-bold text-sky-500 tracking-wider">itta 💭</a>
        <span class="text-xs text-sky-500 font-bold bg-sky-100 px-3 py-1 rounded-full">ログイン不要</span>
    </nav>
    
    <div class="max-w-2xl mx-auto px-4 py-6 flex-grow w-full">
        {% block content %}{% endblock %}
    </div>

    <footer class="bg-white/50 border-t border-sky-100 py-8 mt-12 text-xs text-gray-400">
        <div class="max-w-2xl mx-auto px-4 space-y-2">
            <p class="font-bold text-sky-400">⚠️ おねがい</p>
            <p>1. 投稿された願望（アイデア）は、どなたでも自由に創作の参考にしてOKなものとします。</p>
            <p>2. コメント欄でのやり取りや、外部サイトでの有償依頼等に関するトラブルについて、ittaは責任を負えません。なかよく使ってね！</p>
            <p class="pt-4 text-center text-sky-300">© 2026 itta.</p>
        </div>
    </footer>

</body>
</html>
"""

INDEX_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<div class="mb-6">
    <form action="/" method="GET" class="relative">
        <input type="text" name="q" value="{{ query }}" class="w-full bg-white border-2 border-sky-200 rounded-full py-3 px-5 pr-12 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-100 text-gray-600 placeholder-sky-300 transition" placeholder="🔍 キーワードで願望をさがす...">
        <button type="submit" class="absolute right-4 top-3 text-sky-300 hover:text-sky-500 transition">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </button>
    </form>
</div>

<form method="POST" action="{{ url_for('create_post') }}" class="bg-white p-5 rounded-3xl shadow-sm border border-sky-100 mb-8 relative overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-sky-300 to-blue-300"></div>
    <textarea name="content" rows="3" class="w-full border-0 resize-none focus:ring-0 p-2 mt-2 text-gray-700 placeholder-sky-200 text-lg" placeholder="「こんな絵が見たい！」「〇〇の二次創作が読みたい！」&#13;&#10;あなたの妄想を書き込んでね..." required></textarea>
    <div class="border-t border-sky-50 pt-3 flex justify-end">
        <button type="submit" class="bg-sky-400 text-white font-bold px-6 py-2 rounded-full hover:bg-sky-500 transform hover:scale-105 transition shadow-md">つぶやく ✨</button>
    </div>
</form>

{% if query %}
    <p class="mb-4 text-sm text-sky-500 font-bold">「{{ query }}」の検索結果: {{ posts|length }}件</p>
{% endif %}

<div class="space-y-5">
    {% for post in posts %}
        <div class="bg-white p-5 rounded-3xl shadow-sm border border-sky-100 hover:shadow-md transition">
            <div class="text-xs text-sky-400 mb-3 font-bold flex items-center">
                <span class="bg-sky-50 px-2 py-1 rounded-full mr-2">匿名</span>
                {{ post.created_at.strftime('%m/%d %H:%M') }}
            </div>
            <p class="text-base text-gray-700 mb-4 whitespace-pre-wrap leading-relaxed">{{ post.content }}</p>
            
            <div class="flex items-center space-x-6 text-sm border-t border-sky-50 pt-3">
                <a href="{{ url_for('like_post', post_id=post.id) }}" class="flex items-center text-rose-400 hover:text-rose-500 transition font-bold bg-rose-50 px-3 py-1.5 rounded-full">
                    ♥ いいね ({{ post.likes_count }})
                </a>
                <a href="{{ url_for('post_detail', post_id=post.id) }}" class="flex items-center text-sky-500 hover:text-sky-600 transition font-bold bg-sky-50 px-3 py-1.5 rounded-full">
                    💬 コメント ({{ post.comments.count() }})
                </a>
            </div>
        </div>
    {% else %}
        <div class="text-center py-10">
            <p class="text-sky-400 font-bold mb-2">まだ投稿がありません 😢</p>
            <p class="text-sm text-sky-300">最初の妄想を投稿してみてね！</p>
        </div>
    {% endfor %}
</div>
""")

DETAIL_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<div class="mb-4">
    <a href="{{ url_for('index') }}" class="text-sm text-sky-500 hover:text-sky-600 font-bold flex items-center transition">
        <span class="mr-1">←</span> タイムラインにもどる
    </a>
</div>

<div class="bg-white p-6 rounded-3xl shadow-sm border border-sky-100 mb-8 relative overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-sky-300 to-blue-300"></div>
    <div class="text-xs text-sky-400 mb-3 font-bold mt-2">匿名ユーザー · {{ post.created_at.strftime('%m/%d %H:%M') }}</div>
    <p class="text-xl text-gray-700 mb-6 whitespace-pre-wrap leading-relaxed">{{ post.content }}</p>
    <div class="flex items-center border-t border-sky-50 pt-4">
        <a href="{{ url_for('like_post', post_id=post.id) }}" class="text-rose-400 font-bold text-base flex items-center bg-rose-50 px-4 py-2 rounded-full hover:bg-rose-100 transition">
            ♥ いいね ({{ post.likes_count }})
        </a>
    </div>
</div>

<h3 class="font-bold text-lg text-sky-500 mb-4 pl-2 flex items-center">
    <span>💬 アプローチ / コメント</span>
</h3>
<div class="space-y-4 mb-8">
    {% for comment in post.comments %}
        <div class="bg-white p-4 rounded-2xl border border-sky-100 shadow-sm relative">
            <div class="absolute -left-2 top-4 w-4 h-4 bg-white border-b border-l border-sky-100 transform rotate-45"></div>
            <div class="text-xs text-sky-400 mb-2 font-bold">名無しさん · {{ comment.created_at.strftime('%m/%d %H:%M') }}</div>
            <p class="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">{{ comment.content }}</p>
        </div>
    {% else %}
        <p class="text-sm text-sky-400 pl-2 py-4 font-bold bg-sky-50/50 rounded-2xl text-center">まだアプローチはありません。一番乗りで名乗りを上げよう！</p>
    {% endfor %}
</div>

<form method="POST" action="{{ url_for('create_comment', post_id=post.id) }}" class="bg-white p-5 rounded-3xl shadow-sm border border-sky-100">
    <textarea name="content" rows="2" class="w-full border-0 resize-none focus:ring-0 p-2 text-gray-700 placeholder-sky-200 text-sm" placeholder="「これ僕が描きましょうか？（外部URL等）」&#13;&#10;匿名でアプローチを書き込む..." required></textarea>
    <div class="border-t border-sky-50 pt-3 flex justify-end">
        <button type="submit" class="bg-sky-400 text-white font-bold px-5 py-2 rounded-full hover:bg-sky-500 transform hover:scale-105 transition shadow-md">送信する 🚀</button>
    </div>
</form>
""")

# --- ルーティング ---
@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    
    if query:
        posts = Post.query.filter(Post.content.like(f'%{query}%')).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        
    return render_template_string(INDEX_HTML, posts=posts, query=query)

@app.route('/post', methods=['POST'])
def create_post():
    content = request.form.get('content')
    if content and len(content.strip()) > 0:
        new_post = Post(content=content)
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template_string(DETAIL_HTML, post=post)

@app.route('/like/<int:post_id>')
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes_count += 1
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    content = request.form.get('content')
    if content and len(content.strip()) > 0:
        new_comment = Comment(content=content, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
