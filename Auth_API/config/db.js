const mongoose = require('mongoose');
const dotenv = require('dotenv').config();

const { DB_URI } = process.env;

mongoose.set('strictQuery', false); // Tambahkan baris ini untuk mengatasi peringatan

console.log('DB_URI:', DB_URI); // Tambahkan logging ini untuk memastikan DB_URI

const connectDB = async () => {
  try {
    await mongoose.connect(DB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });

    console.log('MongoDB Connected...');
  } catch (err) {
    console.error(err.message);
    // Exit process with failure
    process.exit(1);
  }
};

module.exports = connectDB;
