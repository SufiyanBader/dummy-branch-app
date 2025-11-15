const express = require('express');
const { Pool } = require('pg');
const app = express();
app.use(express.json());

// --- Database Connection ---
// All config is read from environment variables
const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: process.env.DB_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: process.env.DB_PORT || 5432,
});

// --- API Endpoints ---

// Health check
[cite_start]// This checks DB connectivity, as per the bonus suggestion [cite: 91]
app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.status(200).json({ status: 'healthy', database: 'connected' });
  } catch (e) {
    res.status(503).json({ status: 'unhealthy', database: 'disconnected', error: e.message });
  }
});

[cite_start]// Get all loans [cite: 12]
app.get('/api/loans', (req, res) => {
  // Mock data for demo
  res.json([{ id: 1, amount: 1000 }, { id: 2, amount: 2000 }]);
});

[cite_start]// Get specific loan [cite: 13]
app.get('/api/loans/:id', (req, res) => {
  res.json({ id: req.params.id, amount: 1000, applicant: 'Mock User' });
});

[cite_start]// Create new loan [cite: 14]
app.post('/api/loans', (req, res) => {
  res.status(201).json({ id: 3, ...req.body });
});

[cite_start]// Get loan stats [cite: 15]
app.get('/api/stats', (req, res) => {
  res.json({ total_loans: 2, total_value: 3000 });
});

// --- Server Start ---
const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`Loan API listening on port ${port}`);
  console.log(`Log Level: ${process.env.LOG_LEVEL || 'info'}`);
});

module.exports = app; // For testing