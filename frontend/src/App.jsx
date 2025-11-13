// src/App.jsx
import { useState } from "react";
import "./index.css";

function TurnEditor({ lines, setLines }) {
  return (
    <textarea
      rows={8}
      value={lines}
      onChange={(e) => setLines(e.target.value)}
      style={{ width: "100%", fontFamily: "inherit", fontSize: 14 }}
    />
  );
}

export default function App() {
  const [query, setQuery] = useState("Why was the release delayed?");
  const [lines, setLines] = useState(
    `Alice|We still haven't got license approval for Module X.
Bob|Who was supposed to follow up with procurement?
Raj|I thought procurement had it; I didn't get a confirmation.
Carol|If license isn't ready, we should push the release.`
  );

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [highlightIndex, setHighlightIndex] = useState(null);

  async function run() {
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const raw = lines.split("\n").map((line, i) => {
        const parts = line.split("|");
        return {
          turn_idx: i,
          speaker: (parts[0] || "Speaker").trim(),
          time: "",
          text: (parts[1] || parts[0]).trim(),
        };
      });
      const payload = { query, transcript: raw, top_k: 3 };

      const res = await fetch("http://127.0.0.1:8000/explain", {
        method: "POST",
        body: JSON.stringify(payload),
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        // Try to read response body for nicer message
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const json = await res.json();
      setResult(json);
    } catch (err) {
      console.error("Request failed:", err);
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  // Scroll + highlight logic (evidence jumps here)
  function jumpToEvidence(ev) {
    const idx = ev.turn_idx ?? ev.sent_id ?? ev.index ?? 0;
    const el = document.getElementById(`line-${idx}`);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    setHighlightIndex(idx);
    setTimeout(() => setHighlightIndex(null), 2500);
  }

  // Build transcript lines array from textarea (keeps same indexing)
  function transcriptArray() {
    return lines.split("\n").map((line, i) => {
      const parts = line.split("|");
      return {
        turn_idx: i,
        speaker: (parts[0] || "Speaker").trim(),
        text: (parts[1] || parts[0]).trim(),
      };
    });
  }

  // Render transcript lines (with highlight style)
  function renderTranscriptLines() {
    const arr = transcriptArray();
    return arr.map((line, i) => (
      <div
        id={`line-${i}`}
        key={i}
        className={`p-2 rounded transition-all duration-300 ${
          highlightIndex === i ? "bg-yellow-200" : "bg-white"
        }`}
        style={{ marginBottom: 6 }}
      >
        <strong>{line.speaker}</strong>: {line.text}
      </div>
    ));
  }

  // Helper: safe accessors for both old/new API formats
  function getExplanationText(res) {
    if (!res) return "";
    if (res.explanation) return res.explanation;
    // fallback: build a short explanation from top claim (older API)
    if (res.claims && res.claims.length > 0) {
      const c0 = res.claims[0];
      const ct = c0.claim_text ?? c0.candidate?.text ?? c0.claim ?? "";
      return `Likely reason: "${ct}" (score ${ (c0.score ?? 0).toFixed(2) })`;
    }
    return "";
  }

  // Helper to normalize claims array to expected fields
  function getClaims(res) {
    if (!res) return [];
    // new format: claims with claim_text, score, evidence
    if (res.claims && res.claims.length > 0 && res.claims[0].claim_text) return res.claims;
    // older format: result.claims with candidate, score, context
    if (res.claims && res.claims.length > 0 && res.claims[0].candidate) {
      return res.claims.map((it) => ({
        claim_text: it.candidate?.text || "",
        score: it.score || 0,
        evidence: (it.context || []).map((c) => ({
          sent_id: c.sent_id,
          turn_idx: c.turn_idx,
          speaker: c.speaker,
          time: c.time,
          text: c.text,
        })),
      }));
    }
    return [];
  }

  // Copy explanation to clipboard
  function copyExplanation() {
    const txt = getExplanationText(result);
    if (!txt) return;
    navigator.clipboard?.writeText(txt).catch(() => {});
  }

  return (
    <div style={{ margin: 20, maxWidth: 1000 }}>
      <h1>Query-driven Causal Explanation</h1>

      <div style={{ marginBottom: 10 }}>
        <label>
          <strong>Query</strong>
        </label>
        <br />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ width: "100%", padding: 8 }}
        />
      </div>

      <div style={{ marginBottom: 10 }}>
        <label>
          <strong>Transcript (click evidence to highlight)</strong>
        </label>
        <div
          style={{
            background: "#f9f9f9",
            padding: 10,
            borderRadius: 8,
            maxHeight: 220,
            overflowY: "auto",
            marginBottom: 8,
          }}
        >
          {renderTranscriptLines()}
        </div>
      </div>

      <TurnEditor lines={lines} setLines={setLines} />

      <div style={{ marginBottom: 10, marginTop: 12 }}>
        <button
          onClick={run}
          disabled={loading}
          style={{
            padding: "8px 16px",
            marginRight: 8,
            background: "#111",
            color: "white",
            borderRadius: 6,
            border: "1px solid #333",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Running..." : "Get Explanation"}
        </button>

        <button
          onClick={() => {
            setResult(null);
            setError(null);
          }}
          style={{
            padding: "8px 12px",
            borderRadius: 6,
            border: "1px solid #ccc",
            background: "#fff",
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {error && (
        <div style={{ color: "crimson", marginTop: 8 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 20 }}>
          {/* Explanation summary box */}
          <h2>Explanation</h2>
          <div
            style={{
              border: "1px solid #ddd",
              padding: 12,
              borderRadius: 8,
              background: "#111",
              color: "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
              <div style={{ flex: 1 }}>{getExplanationText(result)}</div>
              <div>
                <button
                  onClick={copyExplanation}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 6,
                    border: "none",
                    background: "#333",
                    color: "#fff",
                    cursor: "pointer",
                  }}
                >
                  Copy
                </button>
              </div>
            </div>
          </div>

          {/* Claims & evidence */}
          <h2 style={{ marginTop: 16 }}>Claims & Evidence</h2>
          {getClaims(result).map((c, idx) => (
            <div
              key={idx}
              style={{
                border: "1px solid #ddd",
                padding: 12,
                borderRadius: 8,
                marginBottom: 10,
                background: "#222",
                color: "#fff",
              }}
            >
              <div style={{ fontWeight: 700 }}>{c.claim_text}</div>
              <div style={{ color: "#aaa", fontSize: 13 }}>score: {Number(c.score || 0).toFixed(2)}</div>
              <div style={{ marginTop: 8 }}>
                <strong>Evidence</strong>
                {Array.isArray(c.evidence) && c.evidence.length > 0 ? (
                  c.evidence.map((e, i) => (
                    <div
                      key={i}
                      style={{
                        background: "#fafafa",
                        marginTop: 6,
                        padding: 8,
                        borderRadius: 6,
                        cursor: "pointer",
                      }}
                      onClick={() => jumpToEvidence(e)}
                    >
                      <div style={{ fontSize: 13 }}>
                        <strong>{e.speaker}</strong>: {e.text}
                      </div>
                      <div style={{ fontSize: 12, color: "#666" }}>
                        turn: {e.turn_idx ?? e.sent_id ?? "-"}
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ marginTop: 6, color: "#ccc" }}>No explicit evidence lines found.</div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
