import logging

log = logging.getLogger()

log.setLevel('INFO')

handler = logging.StreamHandler()

handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

log.addHandler(handler)

#from cassandra.cluster import Cluster

#from cassandra import ConsistencyLevel

from cassandra.cluster import Cluster

from cassandra.query import SimpleStatement


def createKeySpace(KEYSPACE):
    cluster = Cluster(contact_points=['192.168.99.100'], port=9042)
    session = cluster.connect()
    log.info("Creating keyspace...")
    try:
        session.execute("""
                        DROP KEYSPACE IF EXISTS %s
                        """ % KEYSPACE)
        session.execute("""
                        CREATE KEYSPACE %s
                        WITH replication = { 'class': 'SimpleStrategy',
                        'replication_factor': '2' }
                        """ % KEYSPACE)
        log.info("setting keyspace...")
        session.set_keyspace(KEYSPACE)

        log.info("creating table...")
        session.execute("""
                        CREATE TABLE predictions (
                        id int,
                        file_name text,
                        prediction int,
                        time double,
                        PRIMARY KEY (id, prediction)
                       )
                        """)
    except Exception as e:
        log.error("Unable to create keyspace")
        log.error(e)
    return session


def insertData(session, id, file_name, prediction, time):
    session.execute("""
                    INSERT INTO mnist.predictions (id, file_name, prediction, time)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (id, file_name, prediction,time)
                    )


def deleteData(session, id):
    session.execute("""
                    DELETE FROM predictions
                    WHERE id=%s;
                    """,
                    (id,)
                    )

