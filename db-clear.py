import sqlite3
import time 


conn = sqlite3.connect('twitter.db', check_same_thread=False)
c = conn.cursor()
HM_DAYS_KEEP = 3
current_ms_time = time.time()*1000
#miliseconds
one_day = 86400 * 1000
del_to = int(current_ms_time - (HM_DAYS_KEEP*one_day))


sql = "DELETE FROM sentiment WHERE unix < {}".format(del_to)
#c.execute(sql)

#c.execute("VACUUM")

conn.commit()
conn.close()

