# [M] PyPDF2 quadratic runtime with malformed PDF missing xref marker

## Summary
Severity: Medium
Advisory: GHSA-jrm6-h9cq-8gqw
CVE: CVE-2023-36810
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-jrm6-h9cq-8gqw
Type: github-advisory

## Affected
- PyPI: `PyPDF2` — affected >=0 <1.27.9

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to unexpected long runtime.
This quadratic runtime blocks the current process and can utilize a single core of the CPU by 100%. It does not affect memory usage.

### Patches
https://github.com/py-pdf/pypdf/pull/808

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
* [PyPDF2 PR #808](https://github.com/py-pdf/pypdf/pull/808)
* [PyPDF2 Issue #582](https://github.com/py-pdf/pypdf/issues/582)

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-jrm6-h9cq-8gqw
- https://nvd.nist.gov/vuln/detail/CVE-2023-36810
- https://github.com/py-pdf/pypdf/issues/582
- https://github.com/py-pdf/pypdf/pull/808
- https://github.com/py-pdf/pypdf/commit/c6c56f550bb384e05f0139c796ba1308837d6373
- https://github.com/py-pdf/pypdf
- https://lists.debian.org/debian-lts-announce/2023/07/msg00019.html
