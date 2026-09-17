# [H] CVE-2026-26828

## Summary
Severity: High
Advisory: CVE-2026-26828
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-26828
Type: osv

## Details
A NULL pointer dereference in the daap_reply_playlists function (src/httpd_daap.c) of owntone-server commit 3d1652d allows attackers to cause a Denial of Service (DoS) via sending a crafted DAAP request to the server

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26828.json
- https://github.com/archersec/security-advisories/blob/master/owntone-server/owntone-server-advisory-2026.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-26828
- https://github.com/owntone/owntone-server/issues/1961
- https://github.com/owntone/owntone-server/commit/9ac54f0b42491c4862791db4c5368ff80c4000d3
