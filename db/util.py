#coding:utf8
"""
Created on 2013-5-8

@author: lan (www.9miao.com)
"""

from dbpool import dbpool
from MySQLdb.cursors import DictCursor
from numbers import Number
from twisted.python import log

def forEachPlusInsertProps(tablename,props):
    assert type(props) == dict
    pkeysstr = str(tuple(props.keys())).replace('\'','`')
    pvaluesstr = ["%s,"%val if isinstance(val,Number) else "'%s',"%val for val in props.values()]
    pvaluesstr = ''.join(pvaluesstr)[:-1]
    sqlstr = """INSERT INTO `%s` %s values (%s);"""%(tablename,pkeysstr,pvaluesstr)
    return sqlstr

def FormatCondition(props):
    items = props.items()
    itemstrlist = []
    for _item in items:
        if isinstance(_item[1],Number):
            sqlstr = " `%s`=%s,"%_item
        else:
            sqlstr = " `%s`='%s',"%(_item[0],_item[1])
        itemstrlist.append(sqlstr)
    sqlstr = ''.join(itemstrlist)
    return sqlstr[:-1]

def forEachUpdateProps(tablename,props,prere):
    """遍历所要修改的属性，以生成sql语句"""
    assert type(props) == dict
    pro = FormatCondition(props)
    pre = FormatCondition(prere).replace(',',' AND')
    sqlstr = """UPDATE `%s` SET %s WHERE %s;"""%(tablename,pro,pre)
    return sqlstr

def EachQueryProps(props):
    """遍历字段列表生成sql语句
    """
    sqlstr = ""
    if props == '*':
        return '*'
    elif type(props) == type([0]):
        for prop in props:
            sqlstr = sqlstr + prop +','
        sqlstr = sqlstr[:-1]
        return sqlstr
    else:
        raise Exception('props to query must be dict')
        return

def forEachQueryProps(sqlstr, props):
    """遍历所要查询属性，以生成sql语句"""
    if props == '*':
        sqlstr += ' *'
    elif type(props) == type([0]):
        i = 0
        for prop in props:
            if(i == 0):
                sqlstr += ' ' + prop
            else:
                sqlstr += ', ' + prop
            i += 1
    else:
        raise Exception('props to query must be list')
        return
    return sqlstr

def GetTableIncrValue(tablename):
    """
    """
    database = dbpool.config.get('db')
    sql = """SELECT AUTO_INCREMENT FROM information_schema.`TABLES` \
    WHERE TABLE_SCHEMA='%s' AND TABLE_NAME='%s';"""%(database,tablename)
    conn = dbpool.connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return result

def ReadDataFromDB(tablename):
    """
    """
    sql = """select * from %s"""%tablename
    conn = dbpool.connection()
    cursor = conn.cursor(cursorclass = DictCursor)
    cursor.execute(sql)
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def DeleteFromDB(tablename,props):
    """从数据库中删除
    """
    prers = FormatCondition(props)
    sql = """DELETE FROM %s WHERE %s ;"""%(tablename,prers)
    conn = dbpool.connection()
    cursor = conn.cursor()
    count = 0
    try:
        count = cursor.execute(sql)
        conn.commit()
    except Exception,e:
        log.err(e)
        log.err(sql)
    cursor.close()
    conn.close()
    return bool(count)

def InsertIntoDB(tablename,data):
    """写入数据库
    """
    sql = forEachPlusInsertProps(tablename,data)
    conn = dbpool.connection()
    cursor = conn.cursor()
    count = 0
    try:
        count = cursor.execute(sql)
        conn.commit()
    except Exception,e:
        log.err(e)
        log.err(sql)
    cursor.close()
    conn.close()
    return bool(count)

def UpdateWithDict(tablename,props,prere):
    """更新记录
    """
    sql = forEachUpdateProps(tablename, props, prere)
    conn = dbpool.connection()
    cursor = conn.cursor()
    count = 0
    try:
        count = cursor.execute(sql)
        conn.commit()
    except Exception,e:
        log.err(e)
        log.err(sql)
    cursor.close()
    conn.close()
    if(count >= 1):
        return True
    return False

def getAllPkByFkInDB(tablename,pkname,props):
    """根据所有的外键获取主键ID
    """
    props = FormatCondition(props)
    sql = """Select `%s` from `%s` where %s"""%(pkname,tablename,props)
    conn = dbpool.connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [key[0] for key in result]

def GetOneRecordInfo(tablename,props):
    """获取单条数据的信息
    """
    props = FormatCondition(props)
    sql = """Select * from `%s` where %s"""%(tablename,props)
    conn = dbpool.connection()
    cursor = conn.cursor(cursorclass = DictCursor)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def GetRecordList(tablename,pkname,pklist):
    """
    """
    pkliststr = ""
    for pkid in pklist:
        pkliststr+="%s,"%pkid
    pkliststr = "(%s)"%pkliststr[:-1]
    sql = """SELECT * FROM `%s` WHERE `%s` IN %s;"""%(tablename,pkname,pkliststr)
    conn = dbpool.connection()
    cursor = conn.cursor(cursorclass = DictCursor)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def DBTest():
    sql = """SELECT * FROM tb_item WHERE characterId=1000001;"""
    conn = dbpool.connection()
    cursor = conn.cursor(cursorclass = DictCursor)
    cursor.execute(sql)
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def getallkeys(key,mem):
    itemss = getAllItems(mem)
    allkeys = set([])
    for item in itemss:
        for _item in item:
            nowlist = set([])
            for _key in _item[1].keys():
                try:
                    keysplit = _key.split(':')
                    pk = keysplit[2]
                except:
                    continue
                if _key.startswith(key) and not pk.startswith('_'):
                    nowlist.add(int(pk))
            allkeys = allkeys.union(nowlist)
    return allkeys

def getAllKeysFromItms(key,itemss):
    allkeys = set([])
    for item in itemss:
        for _item in item:
            nowlist = set([])
            for _key in _item[1].keys():
                try:
                    keysplit = _key.split(':')
                    pk = keysplit[2]
                except:
                    continue
                if _key.startswith(key) and not pk.startswith('_'):
                    nowlist.add(int(pk))
            allkeys = allkeys.union(nowlist)
    return allkeys

def getAllItems(mem):
    """  函数功能：取所有memcached数据，步骤如下：
        stats items : stats items 显示各个slab中item的数目和最老item的年龄(最后一次访问距离现在的秒数)
             STAT items:1:number 3

         stats cachedump slab_id limit_num : 显示某个slab中的前limit_num个key列表, limit_numb=0,取全部
            stats cachedump 7 2
                ITEM copy_test1 [250 b; 1207795754 s]
                ITEM copy_test [248 b; 1207793649 s]stats slabs
    """
    itemsinfo = mem.get_stats('items')
    itemindex = []
    for items in itemsinfo:
        itemindex += [ _key.split(':')[1] for _key in items[1].keys()]
    s = set(itemindex)

    itemss = [mem.get_stats('cachedump %s 0'%i) for i in s]
    return itemss


def getAllPkByFkInMEM(key,fk,mem):

    pass
