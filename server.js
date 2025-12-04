const express = require('express');
const app = express();
const PORT = 3000;

// Middleware to parse form data
app.use(express.urlencoded({ extended: true }));

// --- In-Memory Database ---
let tasks = [];

// --- Helper: Generate HTML String ---
// We use a function to return the HTML so it updates dynamically based on the tasks array
const getHTML = (taskList) => {
    // Generate list items HTML
    const listItems = taskList.map((task, index) => `
        <li>
            <span>${task}</span>
            <form action="/delete" method="POST" style="display:inline;">
                <input type="hidden" name="index" value="${index}">
                <button type="submit" class="delete-btn">Delete</button>
            </form>
        </li>
    `).join('');

    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Single File Todo</title>
        <style>
            body { font-family: sans-serif; max-width: 400px; margin: 40px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { text-align: center; color: #333; }
            form.add-form { display: flex; gap: 10px; margin-bottom: 20px; }
            input[type="text"] { flex-grow: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            button { cursor: pointer; padding: 8px 12px; background: #007bff; color: white; border: none; border-radius: 4px; }
            button:hover { background: #0056b3; }
            ul { list-style: none; padding: 0; }
            li { background: #f9f9f9; border-bottom: 1px solid #eee; padding: 10px; display: flex; justify-content: space-between; align-items: center; }
            li:last-child { border-bottom: none; }
            button.delete-btn { background: #ff4d4d; font-size: 0.8rem; padding: 5px 10px; }
            button.delete-btn:hover { background: #cc0000; }
        </style>
    </head>
    <body>
        <h1>To-Do List</h1>
        
        <form class="add-form" action="/add" method="POST">
            <input type="text" name="task" placeholder="Add a new task..." required autofocus>
            <button type="submit">Add</button>
        </form>

        <ul>
            ${taskList.length === 0 ? '<p style="text-align:center; color:#888;">No tasks yet.</p>' : listItems}
        </ul>
    </body>
    </html>
    `;
};

// --- Routes ---

// 1. Show the page
app.get('/', (req, res) => {
    res.send(getHTML(tasks));
});

// 2. Add a task
app.post('/add', (req, res) => {
    const newTask = req.body.task;
    if (newTask) tasks.push(newTask);
    res.redirect('/');
});

// 3. Delete a task
app.post('/delete', (req, res) => {
    const index = req.body.index;
    if (index !== undefined && tasks[index]) {
        tasks.splice(index, 1);
    }
    res.redirect('/');
});

// --- Start Server ---
app.listen(PORT, () => {
    console.log(`App running at http://localhost:${PORT}`);
});