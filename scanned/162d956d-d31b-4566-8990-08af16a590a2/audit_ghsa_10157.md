# [M] pip Vulnerable to Inclusion of Functionality from Untrusted Control Sphere

## Summary
Severity: Medium
Advisory: GHSA-jp4c-xjxw-mgf9
CVE: CVE-2026-6357
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-jp4c-xjxw-mgf9
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <26.1

## Details
pip prior to version 26.1 would run self-update check functionality after installing wheel files which required importing well-known Python modules names. These module imports were intentionally deferred to increase startup time of the pip CLI. The patch changes self-update functionality to run before wheels are installed to prevent newly-installed modules from being imported shortly after the installation of a wheel package. Users should still review package contents prior to installation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6357
- https://github.com/pypa/pip/pull/13923
- https://github.com/pypa/pip/commit/b369bfc96cc524e00c267e1693290e6599c36bad
- https://github.com/pypa/pip
- https://ichard26.github.io/blog/2026/04/whats-new-in-pip-26.1/#security-fixes
- http://www.openwall.com/lists/oss-security/2026/04/27/7
