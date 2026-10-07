import http from 'k6/http';
import { sleep } from 'k6';

// Sudden spike to test autoscaling / backpressure behaviour.
export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '10s', target: 500 },
    { duration: '1m', target: 500 },
    { duration: '30s', target: 10 },
  ],
};

const BASE = __ENV.TARGET || 'http://localhost:8000';
export default function () {
  http.get(BASE + '/work');
  sleep(0.05);
}
