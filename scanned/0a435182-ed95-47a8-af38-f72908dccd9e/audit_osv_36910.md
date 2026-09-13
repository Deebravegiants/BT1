# [H] CVE-2026-26829

## Summary
Severity: High
Advisory: CVE-2026-26829
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-26829
Type: osv

## Details
A NULL pointer dereference in the safe_atou64 function (src/misc.c) of owntone-server through commit c4d57aa allows attackers to cause a Denial of Service (DoS) via sending a series of crafted HTTP requests to the server.

## References
- https://github.com/archersec/poc/tree/master/owntone-server-2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26829.json
- https://github.com/archersec/security-advisories/blob/master/owntone-server/owntone-server-advisory-2026.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-26829
- https://github.com/owntone/owntone-server/commit/41e3733cccd527918a08cf05694c5493341bb70f
