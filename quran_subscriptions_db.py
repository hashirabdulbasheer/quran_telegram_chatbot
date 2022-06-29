#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3

class QuranSubscriptionsDB:
    
    conn = None

    def __init__(self, db_file):
        self.create_connection(db_file)

    def create_connection(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)
    
    def add_subscription(self, subscription):
        sql = ''' INSERT OR REPLACE INTO subscriptions(chat_id,user_id)
                  VALUES(?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, subscription)
        self.conn.commit()
        return cur.lastrowid
        
    def select_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM subscriptions")
        rows = cur.fetchall()
        chat_ids = []
        for row in rows:
            chat_ids.append(row[0])
        
        return chat_ids
        
    def delete_subscription(self, user_id):
        sql = "DELETE FROM subscriptions WHERE user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()

