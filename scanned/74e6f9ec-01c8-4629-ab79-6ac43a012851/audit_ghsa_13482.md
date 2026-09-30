# [M] Possible Infinite Loop when PdfWriter(clone_from) is used with a PDF

## Summary
Severity: Medium
Advisory: GHSA-wjcc-cq79-p63f
CVE: CVE-2023-46250
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-31
Source: https://github.com/advisories/GHSA-wjcc-cq79-p63f
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=3.7.0 <3.17.0

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop.
This infinite loop blocks the current process and can utilize a single core of the CPU by 100%. It does not affect memory usage.

That is, for example, the case when the pypdf-user manipulates an incoming malicious PDF e.g. by merging it with another PDF or by adding annotations.

### Patches
The issue was fixed with #2264

### Workarounds
If you cannot update your version of pypdf, you should modify `pypdf/generic/_data_structures.py` just like #2264 did.

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-wjcc-cq79-p63f
- https://nvd.nist.gov/vuln/detail/CVE-2023-46250
- https://github.com/py-pdf/pypdf/pull/2264
- https://github.com/py-pdf/pypdf/commit/9b23ac3c9619492570011d551d521690de9a3e2d
- https://github.com/py-pdf/pypdf
