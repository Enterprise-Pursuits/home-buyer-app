import React from "react";
import Select from "react-select";

const COUNTIES = [
  "Benton","Washington","Boone","Carroll","Madison",
  "Newton","Crawford","Franklin","Johnson","Logan",
  "Sebastian","Yell","Scott"
].map(c => ({ value: c, label: c }));

export default function FilterPanel({ filters, onChange, onSearch, onExport }) {
  const set = (key, val) => onChange({ ...filters, [key]: val });

  return (
    <div className="bg-white shadow rounded-xl p-6 space-y-4">
      <h2 className="text-lg font-bold text-gray-700">Filter Records</h2>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">County</label>
        <Select
          isMulti
          options={COUNTIES}
          value={COUNTIES.filter(c => (filters.county || []).includes(c.value))}
          onChange={sel => set("county", sel.map(s => s.value))}
          placeholder="All counties..."
          className="text-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">City</label>
        <input
          type="text"
          className="w-full border rounded-lg px-3 py-2 text-sm"
          placeholder="e.g. Fayetteville"
          value={filters.city || ""}
          onChange={e => set("city", e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">ZIP Code</label>
        <input
          type="text"
          className="w-full border rounded-lg px-3 py-2 text-sm"
          placeholder="e.g. 72701"
          value={filters.zip_code || ""}
          onChange={e => set("zip_code", e.target.value)}
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Sale Date From</label>
          <input type="date" className="w-full border rounded-lg px-3 py-2 text-sm"
            value={filters.date_from || ""}
            onChange={e => set("date_from", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Sale Date To</label>
          <input type="date" className="w-full border rounded-lg px-3 py-2 text-sm"
            value={filters.date_to || ""}
            onChange={e => set("date_to", e.target.value)} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Min Price ($)</label>
          <input type="number" className="w-full border rounded-lg px-3 py-2 text-sm"
            placeholder="0" value={filters.price_min || ""}
            onChange={e => set("price_min", e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Max Price ($)</label>
          <input type="number" className="w-full border rounded-lg px-3 py-2 text-sm"
            placeholder="No limit" value={filters.price_max || ""}
            onChange={e => set("price_max", e.target.value)} />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">Buyer Name</label>
        <input type="text" className="w-full border rounded-lg px-3 py-2 text-sm"
          placeholder="Search by name..."
          value={filters.buyer_name || ""}
          onChange={e => set("buyer_name", e.target.value)} />
      </div>

      <div className="flex gap-3 pt-2">
        <button onClick={onSearch}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg text-sm">
          Search
        </button>
        <button onClick={onExport}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg text-sm">
          Export CSV
        </button>
      </div>
    </div>
  );
}
