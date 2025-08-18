import http from "k6/http";

export let options = {
  vus: 50,
  duration: "30s",
};

export default function () {
  const url = "http://localhost:8000/transactions";
  const payload = JSON.stringify({
    amount: Math.floor(Math.random() * 1000),
    currency: "USD",
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  http.post(url, payload, params);
}
