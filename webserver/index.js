const express = require("express");
const app = express();

const PORT = 3000;
const DATABASE_PATH = "/tmp/noob_server.db";

var sqlite3 = require("sqlite3").verbose();
var server_db = new sqlite3.Database(DATABASE_PATH, sqlite3.OPEN_READWRITE);

app.get("/", (req, res) => {
  res.send(
    "This is a simple webserver for deliverying the OOB message. Please invoke /sendoob/<oobString> to deliver an OOB"
  );
});

app.get("/sendoob/:oobstring", (req, res) => {
  var oobString = req.params.oobstring;
  let buff = Buffer.from(oobString, "base64");
  let text = buff.toString();
  let jsonOob = JSON.parse(text);

  server_db.all(
    "Select * from EphemeralNoob where PeerId = ?",
    [jsonOob.PeerId],
    (err, rows) => {
      let replaced = rows.length > 0;

      server_db.run(
        "Delete from EphemeralNoob where PeerId = ?",
        [jsonOob.PeerId],
        (err) => {
          server_db.run(
            "INSERT INTO EphemeralNoob (PeerId, NoobId, Noob, Hoob, sent_time) VALUES(?,?,?,?,?)",
            [
              jsonOob.PeerId,
              jsonOob.NoobId,
              jsonOob.Noob,
              jsonOob.Hoob,
              jsonOob.sent_time,
            ],
            (err) => {
              if (!err)
                res.send(
                  replaced ? "Replaced existing oob" : "Inserted new oob"
                );
              else res.send(err);
            }
          );
        }
      );
    }
  );
});

app.listen(3000, () =>
  console.log("Simple OOB delivery server listening on 3000")
);

peer_db.all("Select * from EphemeralNoob LIMIT 1", (err, rows) => {
  let pepe = rows;
});
