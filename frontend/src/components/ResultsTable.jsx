import React from "react";

function fmt(price) {
  if (!price) return "—";
  return "$" + Number(price).toLocaleString();
}

export default function ResultsTable({ data, total, page, setPage, limit }) {
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="bg-white shadow rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-bold text-gray-700">
          Results <span className="text-blue-600">({total.toLocaleString()} records)</span>
        </h2>
        <div className="text-sm text-gray-500">
          Page {page + 1} of {totalPages || 1}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              {["Buyer Name","Property Address","City","County","Sale Date",
                "Sale Price","Phone","Email"].map(h => (
                <th key={h} className="px-4 py-3 text-left font-semibold">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.length === 0 && (
              <tr>
                <td colSpan={8} className="text-center py-10 text-gray-400">
                  No records found. Adjust filters and search.
                </td>
              </tr>
            )}
            {data.map(row => (
              <tr key={row.id} className="hover:bg-blue-50 transition-colors">
                <td className="px-4 py-3 font-medium text-gray-800">{row.buyer_name}</td>
                <td className="px-4 py-3 text-gray-600">{row.property_addr}</td>
                <td className="px-4 py-3 text-gray-600">{row.city}</td>
                <td className="px-4 py-3">
                  <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-0.5 rounded-full">
                    {row.county}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{row.sale_date}</td>
                <td className="px-4 py-3 font-semibold text-gray-800">{fmt(row.sale_price)}</td>
                <td className="px-4 py-3 text-gray-600">{row.phone || "—"}</td>
                <td className="px-4 py-3 text-gray-500">{row.email || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="px-6 py-4 border-t flex justify-center gap-2">
          <button disabled={page === 0}
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 rounded border text-sm disabled:opacity-40 hover:bg-gray-100">
            ← Prev
          </button>
          <span className="px-3 py-1 text-sm text-gray-600">
            {page + 1} / {totalPages}
          </span>
          <button disabled={page + 1 >= totalPages}
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 rounded border text-sm disabled:opacity-40 hover:bg-gray-100">
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
