import { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";

const BASE = "http://127.0.0.1:8000/api/alerts/";
const JSON_HEADERS = { "Content-Type": "application/json" };

function beep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    osc.frequency.value = 880;
    osc.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.25);
  } catch {
    /* audio not available */
  }
}

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(new Set());
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(false);
  const [soundOn, setSoundOn] = useState(false);
  const soundRef = useRef(false);
  const lastMax = useRef(null);

  const load = useCallback(async () => {
    try {
      const q = new URLSearchParams();
      if (filter === "helmet" || filter === "mask") q.set("label", filter);
      if (filter === "unreviewed") q.set("reviewed", "false");
      const [a, s] = await Promise.all([
        fetch(`${BASE}?${q}`).then((r) => r.json()),
        fetch(`${BASE}stats/`).then((r) => r.json()),
      ]);
      const maxId = a.length ? Math.max(...a.map((x) => x.id)) : 0;
      if (lastMax.current !== null && maxId > lastMax.current && soundRef.current) beep();
      lastMax.current = Math.max(lastMax.current ?? 0, maxId);
      setAlerts(a);
      setStats(s);
      setError(false);
    } catch {
      setError(true);
    }
  }, [filter]);

  useEffect(() => {
    load();
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, [load]);

  const toggleSound = () => {
    soundRef.current = !soundOn;
    setSoundOn(!soundOn);
    if (!soundOn) beep(); // test sound, also unlocks audio in the browser
  };

  const remove = async (id) => {
    if (!confirm("Delete this alert and its photo?")) return;
    await fetch(`${BASE}${id}/`, { method: "DELETE" });
    load();
  };

  const toggleReviewed = async (a) => {
    await fetch(`${BASE}${a.id}/`, {
      method: "PATCH",
      headers: JSON_HEADERS,
      body: JSON.stringify({ reviewed: !a.reviewed }),
    });
    load();
  };

  const bulkDelete = async () => {
    if (!confirm(`Delete ${selected.size} selected alerts and their photos?`)) return;
    await fetch(`${BASE}bulk_delete/`, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ ids: [...selected] }),
    });
    setSelected(new Set());
    load();
  };

  const toggleSelect = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const selectAll = () =>
    setSelected(selected.size === alerts.length ? new Set() : new Set(alerts.map((a) => a.id)));

  const exportCsv = () => {
    const rows = [["id", "camera", "label", "confidence", "reviewed", "time"]];
    alerts.forEach((a) =>
      rows.push([a.id, a.camera_id, `"${a.label}"`, a.confidence, a.reviewed, a.created_at])
    );
    const blob = new Blob([rows.map((r) => r.join(",")).join("\n")], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "alerts.csv";
    link.click();
  };

  const daysLeft = (a) =>
    Math.max(0, Math.ceil((new Date(a.expires_at) - Date.now()) / 86400000));
  const maxBar = stats ? Math.max(1, ...stats.days.map((d) => d.count)) : 1;

  return (
    <div className="page">
      <header>
        <h1>ATM Security Dashboard</h1>
        <div className="right">
          <button className={soundOn ? "active" : ""} onClick={toggleSound}>
            {soundOn ? "🔔 Sound on" : "🔕 Sound off"}
          </button>
          <span className={error ? "status off" : "status on"}>
            {error ? "Backend offline" : "Live"}
          </span>
        </div>
      </header>

      {stats && (
        <div className="stats">
          <div className="card"><p>Total alerts</p><h2>{stats.total}</h2></div>
          <div className="card"><p>Today</p><h2>{stats.today}</h2></div>
          <div className="card"><p>Unreviewed</p><h2>{stats.unreviewed}</h2></div>
          <div className="card"><p>Helmet / Mask</p><h2>{stats.helmet} / {stats.mask}</h2></div>
          <div className="card wide">
            <p>Last 7 days</p>
            <div className="chart">
              {stats.days.map((d) => (
                <div className="bar-col" key={d.date}>
                  <span>{d.count}</span>
                  <div className="bar" style={{ height: `${(d.count / maxBar) * 60}px` }} />
                  <span>{d.date}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="toolbar">
        <div className="filters">
          {["all", "helmet", "mask", "unreviewed"].map((f) => (
            <button key={f} className={filter === f ? "active" : ""} onClick={() => { setFilter(f); setSelected(new Set()); }}>
              {f[0].toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <div className="filters">
          <button onClick={selectAll}>{selected.size === alerts.length && alerts.length ? "Deselect all" : "Select all"}</button>
          {selected.size > 0 && (
            <button className="danger" onClick={bulkDelete}>Delete selected ({selected.size})</button>
          )}
          <button onClick={exportCsv}>Export CSV</button>
        </div>
      </div>

      <p className="note">Alerts are deleted automatically after 14 days.</p>

      <div className="grid">
        {alerts.length === 0 && <p>No alerts found.</p>}
        {alerts.map((a) => (
          <div className={`alert ${a.reviewed ? "reviewed" : ""}`} key={a.id}>
            <div className="top">
              <input type="checkbox" className="check" checked={selected.has(a.id)} onChange={() => toggleSelect(a.id)} />
              <img src={a.snapshot} alt={a.label} onClick={() => setPreview(a)} />
            </div>
            <div className="info">
              <strong className="tag">{a.label}</strong>
              <span>{a.camera_id}</span>
              <small>{new Date(a.created_at).toLocaleString()}</small>
              <small>Confidence: {Math.round(a.confidence * 100)}%</small>
              <small>Auto-deletes in {daysLeft(a)} days</small>
              <div className="actions">
                <button onClick={() => toggleReviewed(a)}>{a.reviewed ? "✓ Reviewed" : "Mark reviewed"}</button>
                <button className="danger" onClick={() => remove(a.id)}>Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {preview && (
        <div className="modal" onClick={() => setPreview(null)}>
          <img src={preview.snapshot} alt={preview.label} />
        </div>
      )}
    </div>
  );
}