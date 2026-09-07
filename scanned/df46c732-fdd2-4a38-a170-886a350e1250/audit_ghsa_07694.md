# [H] OpenClaw affected by denial of service via unbounded URL-backed media fetch

## Summary
Severity: High
Advisory: GHSA-j27p-hq53-9wgc
CVE: CVE-2026-29609
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-j27p-hq53-9wgc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
### Summary
URL-backed media fetch handling allocated the entire response payload in memory (`arrayBuffer`) before enforcing `maxBytes`, allowing oversized responses to cause memory exhaustion.

### Affected Versions
- `openclaw` (npm): < `2026.2.14`
- `clawdbot` (npm): <= `2026.1.24-3`

### Patched Versions
- `openclaw` (npm): `2026.2.14`

### Fix Commit
- `openclaw/openclaw` `main`: `00a08908892d1743d1fc52e5cbd9499dd5da2fe0`

### Details
Affected component:
- `src/media/input-files.ts` (`fetchWithGuard`)

When `content-length` is missing or incorrect, reading the body via `response.arrayBuffer()` buffers the full payload before a size check can run.

### Proof of Concept
1. Configure URL-based media input.
2. Serve a response larger than `maxBytes` (chunked transfer / no `content-length`).
3. Trigger the `fetchWithGuard` URL fetch path.

Example local server (large response):
```bash
node -e 'require("http").createServer((_,res)=>{res.writeHead(200,{"content-type":"application/octet-stream"});for(let i=0;i<1024;i++)res.write(Buffer.alloc(1024*64));res.end();}).listen(18888)'
```

### Impact
Availability loss via memory pressure from attacker-controlled remote media responses.

### Mitigation
Until a patched release is available, disable URL-backed media inputs (or restrict to a tight hostname allowlist) and use conservative `maxBytes` limits.

### Credits
Reported by @vincentkoc.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j27p-hq53-9wgc
- https://github.com/openclaw/openclaw/commit/00a08908892d1743d1fc52e5cbd9499dd5da2fe0
- https://github.com/openclaw/openclaw
