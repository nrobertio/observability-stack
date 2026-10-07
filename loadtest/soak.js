import http from 'k6/http';
import { sleep } from 'k6';

// Long steady load to surface leaks and slow degradation.
export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '30m', target: 50 },
    { duration: '2m', target: 0 },
  ],
};

const BASE = __ENV.TARGET || 'http://localhost:8000';
export default function () {
  http.get(BASE + '/work');
  sleep(0.2);
}
