# [M] pip's fallback tar extraction doesn't check symbolic links point to extraction directory

## Summary
Severity: Medium
Advisory: GHSA-4xh5-x5gv-qwph
CVE: CVE-2025-8869
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-4xh5-x5gv-qwph
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <25.3

## Details
When extracting a tar archive pip may not check symbolic links point into the extraction directory if the tarfile module doesn't implement PEP 706. Note that upgrading pip to a "fixed" version for this vulnerability doesn't fix all known vulnerabilities that are remediated by using a Python version that implements PEP 706. Note that this is a vulnerability in pip's fallback implementation of tar extraction for Python versions that don't implement PEP 706 and therefore are not secure to all vulnerabilities in the Python 'tarfile' module. If you're using a Python version that implements PEP 706 then pip doesn't use the "vulnerable" fallback code. Mitigations include upgrading to a version of pip that includes the fix, upgrading to a Python version that implements PEP 706 (Python >=3.9.17, >=3.10.12, >=3.11.4, or >=3.12), applying the linked patch, or inspecting source distributions (sdists) before installation as is already a best-practice.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8869
- https://github.com/pypa/pip/pull/13550
- https://github.com/pypa/pip/commit/f2b92314da012b9fffa36b3f3e67748a37ef464a
- https://github.com/pypa/pip
- https://lists.debian.org/debian-lts-announce/2025/10/msg00028.html
- https://mail.python.org/archives/list/security-announce@python.org/thread/IF5A3GCJY3VH7BVHJKOWOJFKTW7VFQEN
- https://pip.pypa.io/en/stable/news/#v25-2
