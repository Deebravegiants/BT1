# [H] Activepieces: V8 Isolate Sandbox Bypass via importFresh Module Loading

## Summary
Severity: High
Advisory: CVE-2026-73083
Aliases: GHSA-gr3h-c2j7-r52g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73083
Type: osv

## Details
Activepieces is an open source AI workflow automation platform. Prior to 0.80.0, in SANDBOX_CODE_ONLY mode, the engine loads the compiled user module with importFresh(), a wrapper around Node.js require(), before the V8 isolate is applied. Top-level module code can therefore call require('child_process'), access fs, and use other Node.js APIs in the host engine process outside the sandbox. An authenticated user who can create a Code step can read environment secrets including AP_ENCRYPTION_KEY and AP_JWT_SECRET, read or write files, and reach internal services. This issue is fixed in version 0.80.0.

## References
- https://github.com/activepieces/activepieces/releases/tag/0.80.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73083.json
- https://github.com/activepieces/activepieces/security/advisories/GHSA-gr3h-c2j7-r52g
- https://nvd.nist.gov/vuln/detail/CVE-2026-73083
