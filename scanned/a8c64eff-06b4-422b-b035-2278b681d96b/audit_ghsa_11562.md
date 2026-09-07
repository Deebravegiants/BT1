# [C] Feathers has a NoSQL Injection via WebSocket id Parameter in MongoDB Adapter

## Summary
Severity: Critical
Advisory: GHSA-p9xr-7p9p-gpqx
CVE: CVE-2026-29793
CWE: CWE-943
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-p9xr-7p9p-gpqx
Type: github-advisory

## Affected
- npm: `@feathersjs/mongodb` — affected >=5.0.0 <5.0.42

## Details
Socket.IO clients can send arbitrary JavaScript objects as the id argument to any service method (get, patch, update, remove). The transport layer performs no type checking on this argument. When the service uses the MongoDB adapter, these objects pass through getObjectId() and land directly in the MongoDB query as operators. Sending {$ne: null} as the id matches every document in the collection.

## References
- https://github.com/feathersjs/feathers/security/advisories/GHSA-p9xr-7p9p-gpqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-29793
- https://github.com/feathersjs/feathers
