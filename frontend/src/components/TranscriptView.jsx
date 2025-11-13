import React, { useEffect, useRef } from "react";

/**
 * TranscriptView
 *
 * Props:
 * - transcript: array of { turn_idx, speaker, time, text }
 * - highlightIndex: number | null  (index/turn_idx to highlight)
 * - onLineClick: function(line)    (called when a line is clicked)
 * - className: optional string
 */
export default function TranscriptView({
  transcript = [],
  highlightIndex = null,
  onLineClick = () => {},
  className = "",
}) {
  const containerRef = useRef(null);

  // Scroll into view when highlightIndex changes
  useEffect(() => {
    if (highlightIndex === null || highlightIndex === undefined) return;
    const el = document.getElementById(`line-${highlightIndex}`);
    if (el && containerRef.current) {
      const top = el.offsetTop - containerRef.current.offsetTop - containerRef.current.clientHeight / 2 + el.clientHeight / 2;
      containerRef.current.scrollTo({ top, behavior: "smooth" });
      // briefly add a focus style by toggling a CSS class handled by inline classes below
    }
  }, [highlightIndex]);

  function initials(name = "") {
    const parts = name.trim().split(/\s+/);
    if (parts.length === 0) return "?";
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }

  function avatarColor(name = "") {
    // deterministic pastel color from name hash
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h << 5) - h + name.charCodeAt(i);
    const hue = Math.abs(h) % 360;
    return `hsl(${hue} 70% 55%)`;
  }

  function handleCopy(text) {
    navigator.clipboard?.writeText(text).catch(() => {});
  }

  return (
    <div
      ref={containerRef}
      className={`overflow-auto max-h-96 p-2 space-y-2 border rounded-lg bg-white/3 ${className}`}
    >
      {transcript.map((t, i) => {
        const idx = t.turn_idx ?? i;
        const isHighlighted = highlightIndex !== null && highlightIndex === idx;
        return (
          <div
            id={`line-${idx}`}
            key={idx}
            onClick={() => onLineClick(t)}
            className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-shadow
              ${isHighlighted ? "ring-2 ring-yellow-300 bg-yellow-200/30 shadow-sm" : "hover:bg-white/5"}
            `}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") onLineClick(t);
            }}
          >
            <div
              className="flex-shrink-0 rounded-full w-10 h-10 flex items-center justify-center text-sm font-semibold text-white"
              style={{ background: avatarColor(t.speaker || String(idx)) }}
              aria-hidden
            >
              {initials(t.speaker || `S${idx}`)}
            </div>

            <div className="flex-1">
              <div className="flex items-baseline justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="text-sm font-medium">{t.speaker || "Speaker"}</div>
                  {t.time ? <div className="text-xs text-gray-400">{t.time}</div> : null}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    title="Copy text"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopy(t.text || "");
                    }}
                    className="text-xs px-2 py-1 border rounded-md text-gray-500 hover:text-gray-900 hover:bg-white/5"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="mt-1 text-sm text-gray-100 leading-relaxed whitespace-pre-wrap">
                {t.text}
              </div>
            </div>
          </div>
        );
      })}
      {transcript.length === 0 && (
        <div className="text-sm text-gray-400 p-4">No transcript loaded.</div>
      )}
    </div>
  );
}
