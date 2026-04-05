import React, { useState, useRef } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function UploadPanel({ onUploadComplete }) {
  const [files, setFiles]       = useState([]);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const ACCEPTED = ".xlsx,.xls,.pdf";

  const handleFiles = (incoming) => {
    const valid = Array.from(incoming).filter(f =>
      f.name.endsWith(".xlsx") || f.name.endsWith(".xls") || f.name.endsWith(".pdf")
    );
    setFiles(prev => {
      const names = new Set(prev.map(f => f.name));
      return [...prev, ...valid.filter(f => !names.has(f.name))];
    });
    setResult(null);
    setError(null);
  };

  const removeFile = (name) => setFiles(prev => prev.filter(f => f.name !== name));

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleUpload = async () => {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let res;
      if (files.length === 1) {
        const file = files[0];
        const form = new FormData();
        const isExcel = file.name.endsWith(".xlsx") || file.name.endsWith(".xls");
        form.append("file", file);
        res = await axios.post(`${API}/api/upload/${isExcel ? "excel" : "pdf"}`, form, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        const form = new FormData();
        files.forEach(f => form.append("files", f));
        res = await axios.post(`${API}/api/upload/batch`, form, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
      setResult(res.data);
      setFiles([]);
      if (onUploadComplete) onUploadComplete();
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed. Check file format and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-xl p-6 space-y-4">
      <h2 className="text-lg font-bold text-gray-700">Batch Upload Records</h2>
      <p className="text-xs text-gray-500">
        Import homebuyer records from county assessor Excel exports or PDF deed reports.
        Accepts <strong>.xlsx</strong>, <strong>.xls</strong>, and <strong>.pdf</strong> files.
      </p>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
          dragging ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
        }`}
      >
        <div className="text-3xl mb-2">📂</div>
        <p className="text-sm text-gray-600 font-medium">
          Drag & drop files here or <span className="text-blue-600 underline">browse</span>
        </p>
        <p className="text-xs text-gray-400 mt-1">Excel (.xlsx, .xls) or PDF — multiple files supported</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          multiple
          className="hidden"
          onChange={e => handleFiles(e.target.files)}
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map(f => (
            <div key={f.name} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 text-sm">
              <span className="truncate text-gray-700">
                {f.name.endsWith(".pdf") ? "📄" : "📊"} {f.name}
              </span>
              <button
                onClick={() => removeFile(f.name)}
                className="text-red-400 hover:text-red-600 ml-2 flex-shrink-0"
              >✕</button>
            </div>
          ))}
        </div>
      )}

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!files.length || loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-2 rounded-lg text-sm transition-colors"
      >
        {loading ? "Importing..." : `Import ${files.length || ""} File${files.length !== 1 ? "s" : ""}`}
      </button>

      {/* Result */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800">
          <p className="font-semibold">Import complete!</p>
          <p>Records added: <strong>{result.total_added ?? result.added ?? 0}</strong></p>
          <p>Duplicates skipped: <strong>{result.total_skipped ?? result.skipped ?? 0}</strong></p>
          {result.columns_detected && (
            <p className="text-xs text-green-600 mt-1">Columns mapped: {result.columns_detected.join(", ")}</p>
          )}
          {result.errors?.length > 0 && (
            <p className="text-xs text-red-600 mt-1">Errors: {result.errors.join("; ")}</p>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Info box */}
      <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 text-xs text-blue-700 space-y-1">
        <p className="font-semibold">Supported column names:</p>
        <p>Buyer Name · Property Address · City · ZIP · County · Sale Date · Sale Price · Phone · Email · Parcel ID · Seller</p>
        <p className="text-blue-500 mt-1">Column names are flexible — the app will auto-detect common variations.</p>
      </div>
    </div>
  );
}
