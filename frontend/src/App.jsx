import React, { useState, useEffect } from "react";
import FilterPanel from "./components/FilterPanel";
import ResultsTable from "./components/ResultsTable";
import UploadPanel from "./components/UploadPanel";
import { fetchHomebuyers, exportCSV } from "./api";

const LIMIT = 100;

export default function App() {
  const [filters,  setFilters]  = useState({});
  const [data,     setData]     = useState([]);
  const [total,    setTotal]    = useState(0);
  const [page,     setPage]     = useState(0);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  const search = async (pg = 0) => {
    setLoading(true);
    setError(null);
    try {
      const params = { ...filters, skip: pg * LIMIT, limit: LIMIT };
      const res = await fetchHomebuyers(params);
      setData(res.data.results);
      setTotal(res.data.total);
      setPage(pg);
    } catch (e) {
      setError("Failed to fetch records. Is the API running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { search(page); }, [page]);

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-700 text-white px-8 py-5 shadow-md">
        <h1 className="text-2xl font-bold">🏠 NWA New Homebuyer Tracker</h1>
        <p className="text-blue-200 text-sm mt-1">
          13-County Arkansas New Home Purchase Records — Benton, Washington, Boone,
          Carroll, Madison, Newton, Crawford, Franklin, Johnson, Logan, Sebastian, Yell, Scott
        </p>
      </header>

      <main className="max-w-screen-xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        <aside className="lg:col-span-1 space-y-6">
          <FilterPanel
            filters={filters}
            onChange={setFilters}
            onSearch={() => search(0)}
            onExport={() => exportCSV(filters)}
          />
          <UploadPanel onUploadComplete={() => search(0)} />
        </aside>

        <section className="lg:col-span-3 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          {loading ? (
            <div className="bg-white shadow rounded-xl p-20 text-center text-gray-400 text-lg">
              Loading records...
            </div>
          ) : (
            <ResultsTable
              data={data}
              total={total}
              page={page}
              setPage={(fn) => { const np = fn(page); search(np); }}
              limit={LIMIT}
            />
          )}
        </section>
      </main>
    </div>
  );
}
