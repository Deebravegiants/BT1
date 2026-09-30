# [H] CVE-2026-30404

## Summary
Severity: High
Advisory: CVE-2026-30404
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-30404
Type: osv

## Details
The backend database management connection test feature in wgcloud v3.6.3 has a server-side request forgery (SSRF) vulnerability. This issue can be exploited to make the server send requests to probe the internal network, remotely download malicious files, and perform other dangerous operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30404
- https://github.com/TTTlw1024/qwe/issues/3
- https://github.com/tianshiyeben/wgcloud/issues/98
