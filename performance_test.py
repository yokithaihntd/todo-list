import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import time
from prettytable import PrettyTable
from datetime import datetime

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://avnadmin:AVNS_cj9DXDNOEFwUhUs8HNY@pg-3c94d8b6-tasks-db.e.aivencloud.com:16963/defaultdb?sslmode=require&sslrootcert=path/to/ca.pem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

jwt = JWTManager(app)

with app.app_context():
    db.drop_all() 
    db.create_all()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.title}>"

def measure_query_time(query_func, *args, **kwargs):
    """Measures the execution time of a query function."""
    start_time = time.time()
    query_func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time

def test_insert(n):
    """Tests inserting records into the database."""
    tasks = [Task(title=f"Task {i}", description=f"Description for task {i}", completed=False) for i in range(n)]
    db.session.bulk_save_objects(tasks)
    db.session.commit()

def test_select():
    """Tests selecting all records from the tasks table."""
    return Task.query.all()

def test_update():
    """Tests updating records."""
    task = Task.query.first()
    task.title = "Updated Title"
    db.session.commit()

def test_delete():
    """Tests deleting records."""
    task = Task.query.first()
    db.session.delete(task)
    db.session.commit()

def benchmark_operations():
    """Runs benchmarks for each operation with different numbers of records."""
    results = {}

    for n in [1000, 10000, 100000, 1000000]:
        print(f"Running tests with {n} records...")

        start_insert = time.time()
        insert_time = measure_query_time(test_insert, n)
        results[f"Insert {n}"] = {"time": insert_time, "start": start_insert}

        start_select = time.time()
        select_time = measure_query_time(test_select)
        results[f"Select {n}"] = {"time": select_time, "start": start_select}

        start_update = time.time()
        update_time = measure_query_time(test_update)
        results[f"Update {n}"] = {"time": update_time, "start": start_update}

        start_delete = time.time()
        delete_time = measure_query_time(test_delete)
        results[f"Delete {n}"] = {"time": delete_time, "start": start_delete}

    return results

def print_benchmark_results(results):
    print("\nBenchmark Results:")
    table = PrettyTable()
    table.field_names = ["Operation", "Time (s)", "Start Time (s)"]
    for operation, data in results.items():
        table.add_row([operation, f"{data['time']:.5f}", data['start']])
    print(table)

with app.app_context():
    benchmark_results = benchmark_operations()
    print_benchmark_results(benchmark_results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
