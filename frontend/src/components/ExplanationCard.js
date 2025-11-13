// src/components/ExplanationCard.jsx
export default function ExplanationCard({ claim, onJumpTo, index }) {
  return (
    <div className="p-4 rounded-lg bg-white/3 border border-white/6">
      <div className="flex justify-between items-start">
        <div>
          <div className="font-semibold">{claim.claim}</div>
          <div className="text-sm text-gray-400">score: {claim.score.toFixed(2)}</div>
        </div>
        <div>
          <button onClick={()=>onJumpTo(claim.evidence[0])}
                  className="text-xs px-2 py-1 border rounded-md">Show evidence</button>
        </div>
      </div>

      <div className="mt-3 space-y-2">
        {claim.evidence.map((ev,i)=>(
          <div key={i} className="bg-white/5 p-2 rounded-md">
            <div className="text-sm"><strong>{ev.speaker}</strong>: {ev.text}</div>
            <div className="text-xs text-gray-400">turn: {ev.turn_idx ?? ev.sent_id}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
