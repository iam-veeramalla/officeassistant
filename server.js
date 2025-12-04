import { useState } from 'react';

function App() {
  // State for the list of tasks
  const [tasks, setTasks] = useState([]);
  // State for the input box
  const [input, setInput] = useState('');

  // Function to add a task
  const addTask = (e) => {
    e.preventDefault(); // Stop page refresh
    if (!input.trim()) return; // Prevent empty tasks
    
    setTasks([...tasks, input]);
    setInput(''); // Clear input
  };

  // Function to delete a task
  const deleteTask = (indexToDelete) => {
    setTasks(tasks.filter((_, index) => index !== indexToDelete));
  };

  // --- Inline Styles for Simplicity ---
  const styles = {
    container: { maxWidth: '400px', margin: '50px auto', fontFamily: 'Arial, sans-serif', textAlign: 'center' },
    form: { display: 'flex', gap: '10px', marginBottom: '20px' },
    input: { flexGrow: 1, padding: '10px', fontSize: '16px' },
    addBtn: { padding: '10px 20px', background: '#007bff', color: '#fff', border: 'none', cursor: 'pointer' },
    list: { listStyle: 'none', padding: 0, textAlign: 'left' },
    item: { background: '#f4f4f4', padding: '10px', borderBottom: '1px solid #ddd', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    delBtn: { background: '#ff4d4d', color: '#fff', border: 'none', padding: '5px 10px', cursor: 'pointer', borderRadius: '4px' }
  };

  return (
    <div style={styles.container}>
      <h1>Vite To-Do App</h1>

      <form onSubmit={addTask} style={styles.form}>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Add a new task..." 
          style={styles.input}
        />
        <button type="submit" style={styles.addBtn}>Add</button>
      </form>

      <ul style={styles.list}>
        {tasks.length === 0 ? <p style={{color: '#888'}}>No tasks yet.</p> : null}
        
        {tasks.map((task, index) => (
          <li key={index} style={styles.item}>
            <span>{task}</span>
            <button onClick={() => deleteTask(index)} style={styles.delBtn}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
