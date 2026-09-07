# [H] Allocation of Resources Without Limits or Throttling in Axios

## Summary
Severity: High
Advisory: GHSA-777c-7fjr-54vf
CVE: CVE-2026-44488
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-777c-7fjr-54vf
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.7.0 <1.16.0

## Details
## Summary

Axios versions `1.7.0` through `1.15.x` did not enforce configured request and response size limits when requests were sent with the `fetch` adapter. Applications that selected `adapter: 'fetch'`, or ran in environments where axios resolved to the fetch adapter, could receive or send bodies larger than `maxContentLength` or `maxBodyLength` despite those limits being explicitly configured.

This can cause resource exhaustion in server-side usage when a malicious or compromised server returns an oversized response, when an attacker can supply a large `data:` URL, or when an application forwards attacker-controlled request bodies through axios while relying on `maxBodyLength` as a boundary.

## Impact

The impact is availability-only. Affected applications may process, buffer, or transmit data beyond the configured limit, potentially exhausting memory, CPU, or network resources.

This does not affect axios’s default unlimited behaviour by itself: `maxContentLength` and `maxBodyLength` default to `-1`. The vulnerability exists when an application has configured finite limits and expects axios to enforce them.

Server-side runtimes are the primary concern. Browser impact is generally constrained by the browser process and browser fetch behavior, and should not be described as server process exhaustion.

## Affected Functionality

Affected functionality includes requests using the built-in `fetch` adapter with finite `maxContentLength` or `maxBodyLength` values.

Relevant configurations include:

- `adapter: 'fetch'`
- `adapter: ['fetch', ...]` when `fetch` is selected
- environments where neither `xhr` nor `http` is available and axios falls back to `fetch`
- custom fetch environments configured through `env.fetch`

Unaffected functionality includes:

- Node.js default `http` adapter enforcement
- versions before the fetch adapter was introduced
- configurations that do not rely on finite axios size limits

## Technical Details

In vulnerable versions, `lib/adapters/fetch.js` destructured request config without `maxContentLength` or `maxBodyLength`. The adapter dispatched `fetch()` and then materialized the response through `text()`, `arrayBuffer()`, `blob()`, or related resolvers without checking the configured response limit.

The fix in `e5540dc` added:

- `maxContentLength` and `maxBodyLength` reads in `lib/adapters/fetch.js`
- upfront `data:` URL decoded-size checks
- outbound body-size checks before dispatch
- `Content-Length` response pre-checks
- streaming response enforcement
- fallback checks for environments without `ReadableStream`
- regression tests in `tests/unit/adapters/fetch.test.js`

## Proof of Concept of Attack

```js
import http from 'node:http';
import axios from 'axios';

const server = http.createServer((req, res) => {
  let received = 0;

  req.on('data', chunk => {
    received += chunk.length;
  });

  req.on('end', () => {
    res.end(JSON.stringify({ received }));
  });
});

await new Promise(resolve => server.listen(0, resolve));
const url = `http://127.0.0.1:${server.address().port}/`;

await axios.post(url, 'A'.repeat(2 * 1024 * 1024), {
  adapter: 'fetch',
  maxBodyLength: 1024
});

// Vulnerable versions succeed and the server receives 2097152 bytes.
// Fixed versions reject with ERR_BAD_REQUEST.

server.close();
```

## Workarounds

Use the Node.js `http` adapter for server-side requests where finite size limits are security-relevant.

Validate or cap attacker-controlled request bodies before passing them to axios.

Reject or strictly allowlist attacker-controlled URL schemes, especially `data:` URLs, before calling axios.

<details>
<summary>Original Report</summary>

### Summary
When Axios is used with adapter: 'fetch', configured body/response size limits are not enforced. This allows oversized uploads/downloads (including data: URLs) despite explicit limits, which can lead to memory/resource exhaustion in server-side usage.

### Details
maxBodyLength and maxContentLength are not applied in the fetch adapter flow:
  - lib/adapters/fetch.js (146-160): config destructuring does not include these controls.
  - lib/adapters/fetch.js (220-234): request is dispatched with fetch() without request-size enforcement.
  - lib/adapters/fetch.js (267-283): response is materialized via text(), arrayBuffer(), blob(), etc. without response-size checks.
By contrast, the HTTP adapter enforces both limits.

### PoC
  Environment:
  - Axios main at commit f7a4ee2
  - Node v24.2.0

Steps:
  1. Start an HTTP server that counts received bytes and echoes {received}.
  2. Send 2 MiB with:
      - adapter: 'fetch'
      - maxBodyLength: 1024
  3. Request a 4 KiB data: URL with:
      - adapter: 'fetch'
      - maxContentLength: 16

Expected secure behavior: both requests rejected.
 Observed:
  - Upload: success, server received 2097152
  - data: response: success, length 4096

### Impact
Type: DoS / resource exhaustion due to limit bypass.
Impacted: applications using Axios fetch adapter as a server-side security control boundary for untrusted request/response sizes.
</details>

---

## References
- https://github.com/axios/axios/security/advisories/GHSA-777c-7fjr-54vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44488
- https://github.com/axios/axios/pull/10795
- https://github.com/axios/axios/pull/10796
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v1.16.0
