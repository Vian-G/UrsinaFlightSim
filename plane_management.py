from sqlite3 import connect

#############################################################
##################### PLANE MANAGEMENT ######################
#############################################################

class PlaneManager:
    """
    Manages aircraft data and database operations.
    Demonstrates DAO pattern and file I/O for configuration.
    """
    def __init__(self, db_path = "planes.db"):
        self.conn = connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.populate_planes()  # Populate planes right after creation

    def create_table(self):
        """
        Creates the planes table if it doesn't exist.
        Demonstrates SQL schema design with:
        - Primary key with auto-increment
        - Unique constraints
        - Multiple related file paths
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS planes (
                level INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                obj_path TEXT NOT NULL,
                texture_path TEXT NOT NULL,
                description_path TEXT NOT NULL,
                matrix_path TEXT NOT NULL,
                thumbnail_path TEXT NOT NULL
            )""")
        self.conn.commit()

    def add_plane(self, name, obj_path, texture_path, description_path, matrix_path, thumbnail_path):
        """
        Adds a new plane to the database.
        Demonstrates the use of prepared statements for SQL injection prevention.
        """
        self.cursor.execute("""
            INSERT INTO planes (name, obj_path, texture_path, description_path, matrix_path, thumbnail_path)
            VALUES (?, ?, ?, ?, ?, ?)""", (name, obj_path, texture_path, description_path, matrix_path, thumbnail_path))
        self.conn.commit()
        
    def get_all_planes_info(self):
        """
        Retrieves all planes' information from the database.
        Returns a list of tuples containing plane data.
        """
        self.cursor.execute("SELECT level, name, thumbnail_path, description_path FROM planes ORDER BY level")
        return self.cursor.fetchall()

    def get_plane_physics(self, name):
        """
        Retrieves physics-related info of a specific plane by name.
        Used to load 3D model, texture, and flight dynamics matrices.
        """
        self.cursor.execute("SELECT obj_path, texture_path, matrix_path FROM planes WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def populate_planes(self):
        """
        Populates the database with default planes if empty.
        Demonstrates batch data insertion and file path management.
        """
        self.cursor.execute("SELECT COUNT(*) FROM planes")
        if self.cursor.fetchone()[0] ==  0:
            planes = [
                # Each tuple represents: (name, 3D model path, texture path, description file, matrix file, thumbnail)
                ("Cessna-172", "planes/Cessna-172/cessna.obj", "planes/Cessna-172/texture.png", "planes/Cessna-172/desc.txt", "planes/Cessna-172/matrix.txt", "planes/Cessna-172/thumbnail.jpg"),
                ("Boeing-737", "planes/Boeing-737/boeing.bam", "planes/Boeing-737/texture.png", "planes/Boeing-737/desc.txt", "planes/Boeing-737/matrix.txt", "planes/Boeing-737/thumbnail.jpg"),
                ("Spitfire",   "planes/Spitfire/spitfire.obj", "planes/Spitfire/texture.png",   "planes/Spitfire/desc.txt",   "planes/Spitfire/matrix.txt",   "planes/Spitfire/thumbnail.jpg"),
                ("ORCA",       "planes/ORCA/ORCA.bam",         "planes/ORCA/texture.png",       "planes/ORCA/desc.txt",       "planes/ORCA/matrix.txt",       "planes/ORCA/thumbnail.png"),
                ("X-Wing",     "planes/X-Wing/xwing.obj",      "planes/X-Wing/texture.png",     "planes/X-Wing/desc.txt",     "planes/X-Wing/matrix.txt",     "planes/X-Wing/thumbnail.jpg"),]
            for plane in planes:
                self.add_plane(plane[0], plane[1], plane[2], plane[3], plane[4], plane[5])
    
