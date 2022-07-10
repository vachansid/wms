from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
app.config['SQLALCHEMY_BINDS'] = {'two': 'sqlite:///workers.db', 'three': 'sqlite:///works.db'}
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    uname = db.Column(db.String(200), nullable=False)
    pwd = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.id

    def add_worker(self, wr):
        self.workers.append(wr)


class Workers(db.Model):
    __bind_key__ = 'two'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    skill_level = db.Column(db.Integer, nullable=False)
    avail = db.Column(db.Integer)
    n = db.Column(db.Integer)
    d = db.Column(db.Integer)
    d1 = db.Column(db.Integer)
    s_date = db.Column(db.Date)

    def __repr__(self):
        return '<Name %r>' % self.id


class Works(db.Model):
    __bind_key__ = 'three'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    name = db.Column(db.String(200), nullable=False)
    role1 = db.Column(db.String(200))
    n1 = db.Column(db.Integer)
    role2 = db.Column(db.String(200))
    n2 = db.Column(db.Integer)
    role3 = db.Column(db.String(200))
    n3 = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    duration = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200))
    assgn_status = db.Column(db.String(200))


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        comp = request.form.get("company_name")
        email = request.form.get("e_mail")
        user_name = request.form.get("user_name")
        pwd = request.form.get("password")
        if not comp or not email or not user_name or not pwd:
            statment1 = "Some of the fields are empty"
            k = 0
            return render_template("main.html", statment=statment1, comp=comp, email=email, user_name=user_name,
                                   pwd=pwd, k=k)
        usrs = Users.query.order_by(Users.id)
        for user in usrs:
            if user.uname == user_name:
                statment1 = "Account with username '" + user_name + "' already exists."
                k = 0
                return render_template("main.html", statment=statment1, comp=comp, email=email, user_name=user_name,
                                       pwd=pwd, k=k)

        statment1 = "You are sucessfully signed up."
        k = 1
        new_user = Users(cname=comp, email=email, uname=user_name, pwd=pwd)
        db.session.add(new_user)
        db.session.commit()
        return render_template("main.html", statment=statment1, k=k, uid=new_user.id)


@app.route('/account', methods=["POST", "GET"])
def account():
    if request.method == "POST":
        username = request.form.get("user_name")
        password = request.form.get("password")
        usrs = Users.query.order_by(Users.id)
        for user in usrs:
            if user.uname == username:
                if user.pwd == password:
                    return render_template("account.html", user=username, uid=user.id)
                else:
                    return render_template("login.html", statment="Incorrect Password", ur=username)

        return render_template("login.html", statment="Account with username '" + username + "' does not exist")
    else:
        uid = request.args.get("uid")
        user = Users.query.get_or_404(uid)
        today = date.today()
        works = Works.query.order_by(Works.priority)
        for work in works:
            if work.assgn_status == "Assigned" and work.status == "Not Completed":
                today = date.today()
                if (today - work.start_date).days >= work.duration:
                    work_to_edit = Works.query.get_or_404(work.id)
                    work_to_edit.status = "Completed"
                    db.session.commit()
        workers = Workers.query.order_by(Workers.id)
        for worker in workers:
            if worker.avail == 0:
                today = date.today()
                if (today - worker.s_date).days >= worker.d1:
                    worker_to_edit = Workers.query.get_or_404(worker.id)
                    worker_to_edit.avail = 1
                    db.session.commit()
        return render_template("account.html", uid=uid, user=user.uname)


@app.route('/worker', methods=["POST", "GET"])
def worker():
    user = request.args.get("alignment")
    uid = request.args.get("uid")
    if request.method == "GET":
        uid = int(request.args.get("uid"))
        user = Users.query.get_or_404(uid)
        return render_template("worker.html", user=user.uname, uid=uid)
    else:
        uid = int(request.form.get("uid"))
        user = Users.query.get_or_404(uid)
        name = request.form.get("worker_name")
        role = request.form.get("role")
        skill_level = request.form.get("skill_level")
        if not name or not role or skill_level == "0" or len(skill_level) > 2:
            if len(skill_level) == 2 and not (skill_level[0] == '1' and skill_level[1] == '0'):
                return render_template("worker.html", user=user.uname, uid=uid,
                                       statment="Skill Level should be in the range 1-10", wn=name, r=role,
                                       sl=skill_level, k=1)
            else:
                return render_template("worker.html", user=user.uname, uid=uid,
                                       statment="Some of the fields are empty", wn=name, r=role,
                                       sl=skill_level, k=1)
        else:
            new_worker = Workers(name=name, role=role, skill_level=skill_level, uid=uid, avail=1, n=0, d=0, d1=0,
                                 s_date=date.today())
            db.session.add(new_worker)
            db.session.commit()
            return render_template("worker.html", user=user.uname, uid=uid,
                                   statment="New Worker has been added successfully", k=0)


@app.route('/work', methods=["POST", "GET"])
def work():
    if request.method == "GET":
        uid = request.args.get("uid")
        user = Users.query.get_or_404(uid)
        return render_template("work.html", user=user.uname, uid=uid)
    else:
        uid = request.form.get("uid")
        user = Users.query.get_or_404(uid)
        name = request.form.get("work_name")
        role1 = request.form.get("role1")
        n1 = request.form.get("n1")
        role2 = request.form.get("role2")
        n2 = request.form.get("n2")
        role3 = request.form.get("role3")
        n3 = request.form.get("n3")
        sd = request.form.get("date")
        x = sd.split("-")
        duration = request.form.get("duration")
        priority = request.form.get("priority")
        if not name or not sd or not duration or not priority or not (
                (role1 and n1) or (role2 and n2) or (role3 and n3)) or():
            return render_template("work.html", user=user.uname, uid=uid,
                                   statment="Some of the fields are empty", k=1, wn=name, date=sd, dur=duration, prior=priority, r1=role1, r2=role2, r3=role3, n11=n1, n22=n2, n33=n3)
        if date(int(x[0]), int(x[1]), int(x[2])) < date.today():
            return render_template("work.html", user=user.uname, uid=uid,
                                   statment="Please enter a valid start date", k=1, wn=name, date=sd, dur=duration,
                                   prior=priority, r1=role1, r2=role2, r3=role3, n11=n1, n22=n2, n33=n3)
        else:
            if not n1:
                n1 = 0
            if not n2:
                n2 = 0
            if not n3:
                n3 = 0
            start_date = date(int(x[0]), int(x[1]), int(x[2]))
            new_work = Works(uid=uid, name=name, role1=role1, n1=n1, role2=role2, n2=n2, role3=role3, n3=n3,
                             duration=duration,
                             start_date=start_date, assgn_status="Not Assigned", status="Not Completed",
                             priority=priority)
            db.session.add(new_work)
            db.session.commit()
            return render_template("work.html", user=user.uname, uid=uid,
                                   statment="New Work has been added successfully", k=0)


@app.route("/<int:id>", methods=["POST", "GET"])
def update(id):
    worker_to_edit = Workers.query.get_or_404(id)
    user = Users.query.get_or_404(worker_to_edit.uid)
    if request.method == "POST":
        worker_to_edit.name = request.form.get("worker_name")
        worker_to_edit.role = request.form.get("role")
        worker_to_edit.skill_level = request.form.get("skill_level")

        db.session.commit()

        return render_template("account.html", uid=int(worker_to_edit.uid), user=user.uname)

    else:
        return render_template("editworker.html", w=worker_to_edit, user=user.uname)


@app.route("/displayworkers", methods=["POST"])
def display():
    userid = request.form.get("uid")
    uid = int(userid)
    workers = Workers.query.order_by(Workers.id)
    user = Users.query.get_or_404(uid)
    return render_template("displayworkers.html", workers=workers, uid=uid, user=user.uname)


@app.route("/d<int:id>", methods=["POST", "GET"])
def delete(id):
    worker_to_delete = Workers.query.get_or_404(id)
    workers = Workers.query.order_by(Workers.id)
    if request.method == "POST":
        db.session.delete(worker_to_delete)
        db.session.commit()
        userid = int(request.form.get("uid"))
        workers = Workers.query.order_by(Workers.id)
        return render_template("displayworkers.html", workers=workers, uid=userid)
    else:
        workers = Workers.query.order_by(Workers.id)
        return render_template("displayworkers.html", workers=workers)


@app.route("/displayworks", methods=["POST"])
def displayws():
    userid = request.form.get("uid")
    uid = int(userid)
    works = Works.query.order_by(Works.id)
    user = Users.query.get_or_404(uid)
    return render_template("displayworks.html", works=works, uid=uid, user=user.uname)


@app.route("/perform", methods=["POST"])
def perform():
    userid = request.form.get("uid")
    uid = int(userid)
    works = Works.query.order_by(Works.priority)
    workers = Workers.query.order_by(Workers.skill_level)
    for work in works:
        if work.uid == uid and work.assgn_status == "Not Assigned":
            temp1 = 0
            temp1 = work.n1
            temp2 = 0
            temp2 = work.n2
            temp3 = 0
            temp3 = work.n3
            print(temp3)
            ids = []
            for worker in workers:
                if worker.uid == uid and worker.avail == 1:
                    if worker.role == work.role1 and temp1 > 0:
                        temp1 = temp1 - 1
                        ids.append(worker.id)
                    elif worker.role == work.role2 and temp2 > 0:
                        temp2 = temp2 - 1
                        ids.append(worker.id)
                    elif worker.role == work.role3 and temp3 > 0:
                        temp3 = temp3 - 1
                        ids.append(worker.id)

            if temp1 == 0 and temp2 == 0 and temp3 == 0:
                work_to_edit = Works.query.get_or_404(work.id)
                work_to_edit.assgn_status = "Assigned"
                for id in ids:
                    worker_to_edit = Workers.query.get_or_404(id)
                    worker_to_edit.avail = 0
                    worker_to_edit.n = worker_to_edit.n + 1
                    worker_to_edit.d = worker_to_edit.d + work_to_edit.duration
                    worker_to_edit.d1 = work_to_edit.duration
                    worker_to_edit.s_date = work_to_edit.start_date
                    db.session.commit()

            ids.clear()

    user = Users.query.get_or_404(uid)
    return render_template("account.html", uid=uid, user=user.uname, k=1)
