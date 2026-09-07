# [M] Deluge Web-UI vulnerable to XSS through a crafted torrent file

## Summary
Severity: Medium
Advisory: GHSA-5c8p-qhch-qhx6
CVE: CVE-2021-3427
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-5c8p-qhch-qhx6
Type: github-advisory

## Affected
- PyPI: `deluge` — affected >=0 <2.1.0

## Details
The Deluge Web-UI is vulnerable to cross-site scripting through a crafted torrent file. The the data from torrent files is not properly sanitised as it's interpreted directly as HTML. Someone who supplies the user with a malicious torrent file can execute arbitrary Javascript code in the context of the user's browser session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3427
- https://dev.deluge-torrent.org/ticket/3459
- https://github.com/advisories/GHSA-5c8p-qhch-qhx6
- https://github.com/deluge-torrent/deluge
- https://github.com/pypa/advisory-database/tree/main/vulns/deluge/PYSEC-2022-256.yaml
- https://groups.google.com/g/deluge-dev/c/e5zh7wT0rEg
- https://security.gentoo.org/glsa/202210-07
