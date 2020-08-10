var DATABASE_PATH = "";
var sqlite3 = require("sqlite3").verbose();

var db = new sqlite3.Database("/tmp/server_db.db", sqlite3.OPEN_READWRITE);
