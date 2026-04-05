import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8001"
});

export const fetchHomebuyers = (params) =>
  API.get("/api/homebuyers/", { params });

export const fetchCounties = () =>
  API.get("/api/counties");

export const exportCSV = (params) => {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (Array.isArray(v)) v.forEach(val => query.append(k, val));
    else if (v != null && v !== "") query.append(k, v);
  });
  window.open(
    `http://localhost:8001/api/homebuyers/export/csv?${query.toString()}`
  );
};
