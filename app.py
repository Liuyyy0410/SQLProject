import mysql.connector
from flask import Flask, request, jsonify, render_template
from random import randint
import json

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'database': 'db_theatre',
    'user': 'root',
    'password': '041005'
}

def runQuery(query, params=None, fetch=True):
    try:
        db = mysql.connector.connect(**db_config)
        if db.is_connected():
            cursor = db.cursor(buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            db.commit()
            res = []
            if fetch:
                try: res = cursor.fetchall()
                except: res = []
            cursor.close()
            db.close()
            return res
    except Exception as e:
        print(f"DB Error: {e}")
        return None

@app.route('/')
def renderLoginPage():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def verifyAndRenderRespective():
    username = request.form['username']
    password = request.form['password']
    if username in ['cashier', 'manager'] and password == username:
        runQuery('CALL delete_old()', fetch=False)
        return render_template(f'{username}.html')
    return render_template('loginfail.html')

# =======================
#   新功能：会员系统
# =======================

@app.route('/checkMember', methods=['POST'])
def checkMember():
    phone = request.form['phone']
    res = runQuery("SELECT member_id, name, points FROM members WHERE phone = %s", (phone,))
    if res:
        return jsonify({'status': 'found', 'id': res[0][0], 'name': res[0][1], 'points': res[0][2]})
    return jsonify({'status': 'not_found'})

@app.route('/registerMember', methods=['POST'])
def registerMember():
    name = request.form['name']
    phone = request.form['phone']
    try:
        runQuery("INSERT INTO members (name, phone) VALUES (%s, %s)", (name, phone), fetch=False)
        res = runQuery("SELECT member_id FROM members WHERE phone = %s", (phone,))
        return jsonify({'status': 'success', 'id': res[0][0]})
    except:
        return jsonify({'status': 'error', 'msg': '该号码已注册'})

# =======================
#   新功能：小吃系统
# =======================

@app.route('/getSnacks', methods=['GET', 'POST'])
def getSnacks():
    snacks = runQuery("SELECT * FROM snacks")
    data = [{'id': s[0], 'name': s[1], 'price': s[2]} for s in snacks]
    return jsonify(data)

@app.route('/buySnacks', methods=['POST'])
def buySnacks():
    cart = json.loads(request.form['cart'])
    total_cost = 0
    for item in cart:
        snack_id = item['id']
        qty = item['qty']
        if qty > 0:
            price_res = runQuery("SELECT price FROM snacks WHERE snack_id = %s", (snack_id,))
            if price_res:
                price = price_res[0][0]
                total_cost += price * qty
                runQuery("INSERT INTO snack_sales (snack_id, quantity) VALUES (%s, %s)", (snack_id, qty), fetch=False)
    return jsonify({'status': 'success', 'cost': total_cost})

@app.route('/insertSnack', methods=['POST'])
def insertSnack():
    name = request.form['name']
    price = request.form['price']
    runQuery("INSERT INTO snacks (snack_name, price) VALUES (%s, %s)", (name, price), fetch=False)
    return '<h5>小吃添加成功</h5>'

# =======================
#   收银员功能
# =======================

@app.route('/getMoviesShowingOnDate', methods=['POST'])
def moviesOnDate():
    date = request.form['date']
    sql = "SELECT DISTINCT m.movie_id, m.movie_name, s.type FROM movies m JOIN shows s ON m.movie_id = s.movie_id WHERE s.show_date = %s"
    res = runQuery(sql, (date,))
    return render_template('movies.html', movies=res) if res else '<h4>该日期暂无电影上映</h4>'

@app.route('/getTimings', methods=['POST'])
def timingsForMovie():
    date = request.form['date']
    movieID = request.form['movieID']
    movieType = request.form['type']
    sql = """
        SELECT s.time, s.show_id, s.hall_id 
        FROM shows s 
        WHERE s.show_date=%s AND s.movie_id=%s AND s.type=%s
        ORDER BY s.time
    """
    res = runQuery(sql, (date, movieID, movieType))
    timings = []
    for i in res:
        time_int = i[0]
        s_id = i[1]
        h_id = i[2]
        display_text = f"{int(time_int/100)}:{time_int%100:02d} ({h_id}号厅)"
        timings.append((s_id, display_text))
    return render_template('timings.html', timings=timings)

@app.route('/getAvailableSeats', methods=['POST'])
def getSeating():
    showID = request.form['showID']
    sql_hall = "SELECT hs.class, hs.total_seats FROM shows s JOIN hall_seats hs ON s.hall_id = hs.hall_id WHERE s.show_id = %s"
    res_hall = runQuery(sql_hall, (showID,))
    totalGold = totalStandard = 0
    for row in res_hall:
        if row[0] == 'gold': totalGold = row[1]
        elif row[0] == 'standard': totalStandard = row[1]
    sql_booked = "SELECT seat_no FROM booked_tickets WHERE show_id = %s"
    res_booked = runQuery(sql_booked, (showID,))
    booked_set = {r[0] for r in res_booked}
    goldSeats = [[i, 'disabled' if (i + 1000) in booked_set else ''] for i in range(1, totalGold + 1)]
    standardSeats = [[i, 'disabled' if i in booked_set else ''] for i in range(1, totalStandard + 1)]
    return render_template('seating.html', goldSeats=goldSeats, standardSeats=standardSeats)

@app.route('/getPrice', methods=['POST'])
def getPriceForClass():
    showID = request.form['showID']
    seatClass = request.form['seatClass']
    sql = """
        SELECT p.price 
        FROM shows s 
        JOIN price_listing p 
        ON s.type = p.type AND DAYNAME(s.show_date) = p.day 
        WHERE s.show_id = %s
    """
    res = runQuery(sql, (showID,))
    if not res: return '<h5>未找到价格信息</h5>'
    base_price = int(res[0][0])
    final_price = base_price * 1.5 if seatClass == 'gold' else base_price
    return f'<h5>票价: ¥ {int(final_price)}</h5><button onclick="confirmBooking()" class="btn btn-success">确认预订</button>'

@app.route('/insertBooking', methods=['POST'])
def createBooking():
    showID = request.form['showID']
    seatClass = request.form['seatClass']
    rawSeatNo = int(request.form['seatNo'])
    memberID = request.form.get('memberID') 
    
    finalSeatNo = rawSeatNo + 1000 if seatClass == 'gold' else rawSeatNo

    ticketNo = randint(0, 2147483646)
    while runQuery("SELECT ticket_no FROM booked_tickets WHERE ticket_no=%s", (ticketNo,)):
        ticketNo = randint(0, 2147483646)
    
    # 核心修改：只负责插入订单。
    # 积分更新逻辑已移除，由 MySQL 触发器 'trigger_add_points' 自动处理。
    if memberID and memberID != 'null':
        runQuery("INSERT INTO booked_tickets (ticket_no, show_id, seat_no, member_id) VALUES (%s, %s, %s, %s)", 
                 (ticketNo, showID, finalSeatNo, memberID), fetch=False)
        msg_point = "<br><span style='color:#28a745'>会员积分 +10 (触发器自动处理)</span>"
    else:
        runQuery("INSERT INTO booked_tickets (ticket_no, show_id, seat_no) VALUES (%s, %s, %s)", 
                 (ticketNo, showID, finalSeatNo), fetch=False)
        msg_point = ""

    return f'<h5>购票成功</h5><h6>票号: {ticketNo}</h6>{msg_point}'

# =======================
#   经理功能
# =======================

@app.route('/getShowsShowingOnDate', methods=['POST'])
def getShowsOnDate():
    date = request.form['date']
    sql = "SELECT s.show_id, m.movie_name, s.type, s.time FROM shows s JOIN movies m ON s.movie_id = m.movie_id WHERE s.show_date = %s"
    res = runQuery(sql, (date,))
    shows = [[i[0], i[1], i[2], int(i[3]/100), f"{i[3]%100:02d}"] for i in res] if res else []
    return render_template('shows.html', shows=shows) if shows else '<h4>该日期暂无排片</h4>'

@app.route('/getBookedWithShowID', methods=['POST'])
def getBookedTickets():
    showID = request.form['showID']
    sql = """
        SELECT b.ticket_no, b.seat_no, m.name 
        FROM booked_tickets b 
        LEFT JOIN members m ON b.member_id = m.member_id 
        WHERE b.show_id = %s 
        ORDER BY b.seat_no
    """
    res = runQuery(sql, (showID,))
    tickets = []
    if res:
        for t in res:
            t_no, s_no, m_name = t[0], t[1], t[2]
            s_class = 'Gold' if s_no > 1000 else 'Standard'
            display_seat = s_no - 1000 if s_no > 1000 else s_no
            member_str = f" ({m_name})" if m_name else ""
            tickets.append([t_no, f"{display_seat}{member_str}", s_class])
    return render_template('bookedtickets.html', tickets=tickets) if tickets else '<h5>暂无预订</h5>'

@app.route('/fetchMovieInsertForm', methods=['GET'])
def getMovieForm():
    return render_template('movieform.html')

@app.route('/insertMovie', methods=['POST'])
def insertMovie():
    movieName = request.form['movieName']
    movieLen = request.form['movieLen']
    movieLang = request.form['movieLang']
    genres = request.form['types'].split() 
    startShowing = request.form['startShowing']
    endShowing = request.form['endShowing']
    check = runQuery("SELECT * FROM movies WHERE movie_name=%s", (movieName,))
    if check: return '<h5>电影已存在</h5>'
    movieID = randint(0, 2147483646)
    runQuery("INSERT INTO movies VALUES (%s, %s, %s, %s, %s, %s)", 
             (movieID, movieName, movieLen, movieLang, startShowing, endShowing), fetch=False)
    for g in genres:
        runQuery("INSERT INTO movie_genres (movie_id, genre) VALUES (%s, %s)", (movieID, g), fetch=False)
    return f'<h5>电影添加成功</h5><h6>ID: {movieID}</h6>'

@app.route('/getValidMovies', methods=['POST'])
def validMovies():
    showDate = request.form['showDate']
    sql = "SELECT movie_id, movie_name, length, language FROM movies WHERE show_start <= %s AND show_end >= %s"
    movies = runQuery(sql, (showDate, showDate))
    final_movies = []
    if movies:
        for m in movies:
            g_res = runQuery("SELECT genre FROM movie_genres WHERE movie_id = %s", (m[0],))
            genres_str = " ".join([x[0] for x in g_res])
            final_movies.append((m[0], m[1], genres_str, m[2], m[3]))
    return render_template('validmovies.html', movies=final_movies) if final_movies else '<h5>无可用电影</h5>'

@app.route('/getHallsAvailable', methods=['POST'])
def getHalls():
    movieID = request.form['movieID']
    showDate = request.form['showDate']
    showTime = int(request.form['showTime'])
    movieLen = runQuery("SELECT length FROM movies WHERE movie_id = %s", (movieID,))[0][0]
    startMin = int(showTime / 100) * 60 + (showTime % 100)
    endMin = startMin + movieLen
    shows = runQuery("SELECT s.hall_id, m.length, s.time FROM shows s JOIN movies m ON s.movie_id=m.movie_id WHERE s.show_date=%s", (showDate,))
    busy_halls = set()
    for s in shows:
        s_start = int(s[2]/100)*60 + (s[2]%100)
        s_end = s_start + s[1]
        if not (endMin <= s_start or startMin >= s_end):
            busy_halls.add(s[0])
    all_halls = {r[0] for r in runQuery("SELECT hall_id FROM halls")}
    available = list(all_halls - busy_halls)
    return render_template('availablehalls.html', halls=available) if available else '<h5>无可用影厅</h5>'

@app.route('/insertShow', methods=['POST'])
def insertShow():
    runQuery("INSERT INTO shows (show_id, movie_id, hall_id, type, time, show_date) VALUES (%s, %s, %s, %s, %s, %s)",
             (randint(0, 2147483646), request.form['movieID'], request.form['hallID'], 
              request.form['movieType'], request.form['showTime'], request.form['showDate']), fetch=False)
    return '<h5>排片成功</h5>'

@app.route('/deleteShow', methods=['POST'])
def deleteShow():
    runQuery("DELETE FROM shows WHERE show_id = %s", (request.form['showID'],), fetch=False)
    return '<h5>已删除</h5>'

@app.route('/getPriceList', methods=['GET'])
def priceList():
    return render_template('currentprices.html', prices=runQuery("SELECT * FROM price_listing ORDER BY type"))

@app.route('/setNewPrice', methods=['POST'])
def setPrice():
    new_price = request.form['newPrice']
    runQuery("UPDATE price_listing SET price = %s WHERE price_id = %s", (new_price, request.form['priceID']), fetch=False)
    return f'<h5>价格已更新为: ¥ {new_price}</h5>'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
