

# mysqlInfo.py

import pymysql

class dbLink:
    host = ''
    user = ''
    password = ''
    db = ''
    charset = ''
    con = '' 

    def __init__(self): # 초기
        self.host = 'localhost'
        self.user = 'web'
        self.password = '1324'
        self.db = 'telegramBot'
        self.charset = 'utf8'

    def conDb(self): # db연결
        try:
            self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, charset=self.charset);
        except:
            errorCode = "데이터 베이스 연결 실패!"
            print(errorCode)
            return False
        return True


    def dbFetchAll(self, sqlStr): # 모든 결과 배열로 반환
        if (self.conDb() == False):
            return -1
        cur = self.con.cursor() # 커서 객체 생성

        try:
            cur.execute(sqlStr) # SQL문장 실행
        except:
            print("mysql 쿼리문 Fetch all 실행 실패 : ", sqlStr)
            return -1
        rows = cur.fetchall() # 조회된 결과를 모두 리스트 형대로 반환, 데이터가 없는경우 빈 리스트 반환
        self.con.commit() # DB에 반영
        self.con.close() # 접속 해제
        return rows


    def dbFetchOne(self, sqlStr): # 결과 첫 하나만 반환. count등에 유리
        if (self.conDb() == False):
            return -1

        cur = self.con.cursor() # 커서 객체 생성

        try:
            cur.execute(sqlStr) # SQL문장 실행
        except:
            print("mysql 쿼리문 Fetch one 실행 실패 : ", sqlStr)
            return -1
        result = cur.fetchone() # 조회된 결과를 하나 반환
        self.con.commit() # DB에 반영
        self.con.close() # 접속 해제
        return result

    def dbFetchOneWord(self, sqlStr): # 반환받은 리스트에서 첫번째만 반환. 왜만들었더라..
        if (self.conDb() == False):
            return -1

        cur = self.con.cursor() # 커서 객체 생성

        try:
            cur.execute(sqlStr) # SQL문장 실행
        except:
            print("mysql 쿼리문 Fetch one Word 실행 실패 : ", sqlStr)
            return -1
        result = cur.fetchone() # 조회된 결과를 하나 반환
        self.con.commit() # DB에 반영
        self.con.close() # 접속 해제
        return result[0]


    def dbRenew(self, sqlStr): # 값을 반환받지 않고 실행만 시킴. 갱신에 유리
        if (self.conDb() == False):
            return False

        cur = self.con.cursor() # 커서 객체 생성

        try:
            cur.execute(sqlStr) # SQL문장 실행
        except:
            print("mysql 쿼리문 Renew 실행 실패 : ", sqlStr)
            return False
        self.con.commit() # DB에 반영
        self.con.close() # 접속 해제
        return True
