# [M] Axios: HTTP adapter streamed responses bypass maxContentLength

## Summary
Severity: Medium
Advisory: GHSA-vf2m-468p-8v99
CVE: CVE-2026-42036
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-vf2m-468p-8v99
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
### Summary

When responseType: 'stream' is used, Axios returns the response stream without enforcing maxContentLength. This bypasses configured response-size limits and allows unbounded downstream consumption.

### Details
In lib/adapters/http.js:
  - 786-789: for responseType === 'stream', Axios immediately settles with the stream.
  - 797-810: maxContentLength enforcement exists only in the non-stream buffering branch.

So callers may set maxContentLength and still receive/read arbitrarily large streamed responses.

### PoC

Environment:
- Axios main at commit f7a4ee2
- Node v24.2.0

 Steps:

1. Start an HTTP server that returns a 2 MiB response body.
2. Call Axios with:
   - adapter: 'http'
   - responseType: 'stream'
   - maxContentLength: 1024
3. Read the returned stream fully.

Observed:
- Success; full 2097152 bytes readable.

Control check:
- Same endpoint with responseType: 'text' and same maxContentLength: rejected with maxContentLength size of 1024 exceeded.

### Impact
Type: DoS / unbounded response processing.
Impacted: Node.js applications relying on maxContentLength as a safety boundary while using streamed Axios responses.

## References
- https://github.com/axios/axios/security/advisories/GHSA-vf2m-468p-8v99
- https://nvd.nist.gov/vuln/detail/CVE-2026-42036
- https://github.com/axios/axios
