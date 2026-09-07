# [H] linx-server has an issue in the uploadPostHandler component that allows attackers to cause a Denial of Service (DoS) via a crafted POST request

## Summary
Severity: High
Advisory: GHSA-g743-m6x3-v6wm
CVE: CVE-2026-50879
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-g743-m6x3-v6wm
Type: github-advisory

## Affected
- Go: `github.com/andreimarcu/linx-server` — affected >=0

## Details
An issue in the uploadPostHandler component of Andrei Marcu linx-server v2.3.8 allows attackers to cause a Denial of Service (DoS) via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50879
- https://gist.github.com/pyuysig/807d92e6d8e7648d140d004f3b54b08b
- https://github.com/andreimarcu/linx-server
