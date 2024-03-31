# nval – количество дтп для тестов. Для каждого дтп по 2 машины, для каждой машины 2 участника
import psycopg2
from faker import Faker
import argparse
import sys

fake = Faker()

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-nval', '--nvalues', default=5)
    parser.add_argument('-dbname', default="course_db")
    parser.add_argument('-user', default='dmitrijzigunov')
    parser.add_argument('-password', default='dmitrijzigunov')
 
    return parser

# Функция для подключения к БД
def connect_to_db(conn_params):
    try:
        connection = psycopg2.connect(
            dbname=conn_params["dbname"],
            user=conn_params["user"],
            password=conn_params["password"],
            host="localhost",
            port=5432
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

def print_test(nm, description, status = None):
    if status is True:
        if description == "":
            print(f"TEST passed ({nm})")
        else:
            print(f"TEST passed ({nm}): {description}")
    elif status is False:
        print(f"TEST failed ({nm}): {description}")
    else:
        print(f"({nm}): {description}")

# Функция для вставки строк в таблицы
def insert_rows(connection, nval):
    try:
        cursor = connection.cursor()
        for idtp in range(nval):
            # Генерация данных для DTP
            description = fake.text(max_nb_chars=100)
            datetime = fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None)
            coord_w = fake.pyfloat(positive=True, min_value=50, max_value=60)
            coord_l = fake.pyfloat(positive=True, min_value=50, max_value=60)
            dor = fake.text(max_nb_chars=200)
            osv = fake.text(max_nb_chars=50)
            count_ts = 2
            count_parts = 4

            cursor.execute(
                "INSERT INTO DTP (id, description, datetime, coord_w, coord_l, dor, osv, count_ts, count_parts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (idtp, description, datetime, coord_w, coord_l, dor, osv, count_ts, count_parts)
            )
            
            # Генерация данных для VEHICLE
            for iveh in range(2):  # Вставляем по две записи для каждого DTP
                marka_ts = fake.text(max_nb_chars=100)
                m_ts = fake.text(max_nb_chars=100)
                r_rul = fake.text(max_nb_chars=50)
                type_ts = fake.text(max_nb_chars=200)
                car_year = fake.random_int(min=1900, max=2022)
                color = fake.text(max_nb_chars=15)

                cursor.execute(
                    "INSERT INTO VEHICLE (id, dtp_id, marka_ts, m_ts, r_rul, type_ts, car_year, color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (iveh + idtp * 2, idtp, marka_ts, m_ts, r_rul, type_ts, car_year, color)
                )
                
                vehicle_id = cursor.lastrowid  # Получаем id вставленной строки в VEHICLE
                
                # Генерация данных для PARTICIPANT
                for iprtc in range(2):  # Вставляем по две записи для каждого VEHICLE
                    category = fake.text(max_nb_chars=50)
                    warnings = fake.text(max_nb_chars=400)
                    safety_belt = fake.boolean()
                    pol = fake.text(max_nb_chars=15)
                    health = fake.text(max_nb_chars=200)

                    cursor.execute(
                        "INSERT INTO PARTICIPANT (id, vehicle_id, category, warnings, safety_belt, pol, health) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (iprtc + (iveh + idtp * 2) * 2, iveh, category, warnings, safety_belt, pol, health)
                    )

            connection.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        print("Error inserting data into tables:", error)
        return False


# Функция для вставки и проверки вставленных строк
def checking_insert_rows(name_test, connection, nval):
    if not insert_rows(connection, nval):
        print_test(name_test, "Inserting data into DTP table", False)
        return False

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM DTP")
        record = cursor.fetchone()
        count_after_insert = record[0]
        if count_after_insert != nval:
            print_test(name_test, "Number of rows after insertion does not match with expected value", False)
            return False
    except (Exception, psycopg2.Error) as error:
        print_test(name_test, "Error testing insertion –" + str(error), False)
        return False
    return True

# Функция для удаления значений
def delete_rows(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM PARTICIPANT")
        cursor.execute("DELETE FROM VEHICLE")
        cursor.execute("DELETE FROM DTP")
        connection.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        print_test(False, "Error deleting data from DTP table " + str(error))
        return False
    
def checking_delete_rows(name_test, connection):
    if not delete_rows(connection):
        print_test(name_test, "Deleting data from DTP table", False)
        return False

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM DTP")
        record = cursor.fetchone()
        count_after_delete = record[0]
        if count_after_delete != 0:
            print_test(name_test, "Number of rows after deletion is not zero", False)
            return False
    except (Exception, psycopg2.Error) as error:
        print_test(name_test, "Error testing deletion " + str(error), False)
        return False

    return True



# TODO ФУНКЦИИ ТЕСТЫ
# Функция для выполнения теста добавления и удаления строк
def test_insert_and_delete(connection, nval):
    name = "insert and delete"

    if not checking_insert_rows(name, connection, nval):
        return False
    if not checking_delete_rows(name, connection):
        return False
    
    print_test(name, "", True)
    return True
# Функция для проверки работы join dv
def checking_join_dv(connection, nval):
    name = "join dtp-vehicle"
    result_test = True
    
    if not checking_insert_rows(name, connection, nval):
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT v.id FROM VEHICLE v JOIN DTP d ON v.dtp_id = d.id"
        )
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) > 0:
            result_test = True
        else:
            print_test(name, "No rows returned from join query", False)
            result_test = False
    except Exception as e:
        print_test(name, f"Join query failed: {str(e)}", False)
        result_test = False
    
    if not checking_delete_rows(name, connection):
        result_test = False
    
    print_test(name, "", True)
    return result_test
# Функция для проверки работы join vp
def checking_join_vp(connection, nval):
    name = "join vehicle-participant"
    result_test = True
    
    if not checking_insert_rows(name, connection, nval):
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT p.id FROM PARTICIPANT p JOIN VEHICLE v ON p.vehicle_id = v.id"
        )
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) > 0:
            result_test = True
        else:
            print_test(name, "No rows returned from join query", False)
            result_test = False
    except Exception as e:
        print_test(name, f"Join query failed: {str(e)}", False)
        result_test = False
    
    if not checking_delete_rows(name, connection):
        result_test = False
    
    print_test(name, "", True)
    return result_test



# Функция для запуска тестов
def run_tests(conn_params):
    connection = connect_to_db(conn_params)
    if connection:
        print("Tests for", conn_params["nval"], "entities");
        val = test_insert_and_delete(connection, conn_params["nval"])
        if not val:
            return 1
        val = checking_join_dv(connection, conn_params["nval"])
        if not val:
            return 1
        val = checking_join_vp(connection, conn_params["nval"])
        if not val:
            return 1
        else:
            print("All tests passed successfully")
            return 0  # успешное завершение
    else:
        print("Failed to connect to the database")
        sys.exit(1)


if __name__ == "__main__":
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    conn_params = {"nval": namespace.nvalues,"dbname": namespace.dbname, 
                   "user": namespace.user, "password": namespace.password}
    conn_params["nval"] = int(conn_params["nval"]) 
    
    run_tests(conn_params)