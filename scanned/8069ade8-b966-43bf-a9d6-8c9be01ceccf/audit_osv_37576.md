# [M] LibreChat Denial of Service (DoS) via Unhandled Exception in DELETE /api/convos

## Summary
Severity: Medium
Advisory: CVE-2026-31949
Aliases: GHSA-5m32-chq6-232p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31949
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Prior to 0.8.3-rc1, a Denial of Service (DoS) vulnerability exists in the DELETE /api/convos endpoint that allows an authenticated attacker to crash the Node.js server process by sending malformed requests. The DELETE /api/convos route handler attempts to destructure req.body.arg without validating that it exists. The server crashes due to an unhandled TypeError that bypasses Express error handling middleware and triggers process.exit(1). This vulnerability is fixed in 0.8.3-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31949.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-5m32-chq6-232p
- https://nvd.nist.gov/vuln/detail/CVE-2026-31949
