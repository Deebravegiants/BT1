# [C] OpenChamber 1.11.7 Unauthenticated RCE via /api/fs/exec

## Summary
Severity: Critical
Advisory: CVE-2026-53975
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-53975
Type: osv

## Details
OpenChamber 1.11.7 contains an unauthenticated remote code execution vulnerability that allows remote attackers to execute arbitrary shell commands by sending crafted POST requests to the /api/fs/exec endpoint, which passes commands verbatim to Node.js spawn() without any allowlist, blocklist, or argument validation. The authentication middleware becomes a no-op when UI_PASSWORD is not configured, matching the default Docker deployment, enabling attackers to execute arbitrary OS commands as the application user and retrieve full command output including stdout, stderr, and exit code from the server response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53975.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53975
- https://www.vulncheck.com/advisories/openchamber-unauthenticated-rce-via-api-fs-exec
- https://github.com/openchamber/openchamber/commit/f1b9506132faf6c564a2694c7f33b94421a49b4a
- https://github.com/openchamber/openchamber
