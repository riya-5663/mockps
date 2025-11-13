// src/components/QueryForm.jsx
export default function QueryForm({ query, setQuery, lines, setLines, onRun, loading }) {
  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="md:col-span-1">
        <label className="block text-sm font-medium mb-1">Query</label>
        <input value={query} onChange={e=>setQuery(e.target.value)}
               className="w-full rounded-lg px-3 py-2 bg-white/5 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <div className="mt-3">
          <button onClick={onRun} disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 disabled:opacity-60">
            {loading ? "Running…" : "Get Explanation"}
          </button>
        </div>
      </div>

      <div className="md:col-span-2">
        <label className="block text-sm font-medium mb-1">Transcript (speaker|text)</label>
        <textarea rows={8} value={lines} onChange={e=>setLines(e.target.value)}
          className="w-full rounded-lg p-3 bg-white/5 resize-vertical" />
      </div>
    </div>
  );
}
