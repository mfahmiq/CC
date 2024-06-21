const express = require('express');
const bodyParser = require('body-parser');
require('dotenv').config();
const connectDB = require('./config/db');

const news = require('./routes/news');
const users = require('./routes/users');
const model = require('./routes/model');
const PORT = process.env.PORT || 8080;
const HOST = process.env.HOST || '0.0.0.0'; 

const app = express();

console.log('DB_URI:', process.env.DB_URI); // Logging tambahan untuk debugging

connectDB();

app.use(bodyParser.json());

app.use("/users", users);
app.use("/model", model);
app.use("/news", news);

app.get("/", (req, res) => res.send("Welcome to the Users API!"));
app.all("*", (req, res) => res.send("You've tried reaching a route that doesn't exist."));


    app.listen(PORT, HOST, () => console.log(`Server running on http://${HOST}:${PORT}`));

