const express = require('express');
const auth = require('../middleware/auth');
const router = express.Router();
const { uploadAndPredict, getHistory, deletePrediction } = require("../controllers/modelAi");
const Multer = require('multer');
const path = require('path');
const fs = require('fs');

const upload = Multer({ dest: 'uploads/' });

router.post('/predict',auth, upload.single('image'), uploadAndPredict);
router.get('/history', auth, getHistory);
router.delete('/predictions/:id', auth, deletePrediction);

module.exports = router;
