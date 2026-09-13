# [H] Pycel allows code injection via a crafted formula

## Summary
Severity: High
Advisory: GHSA-pw67-xjhq-389w
CVE: CVE-2024-53924
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-17
Source: https://github.com/advisories/GHSA-pw67-xjhq-389w
Type: github-advisory

## Affected
- PyPI: `pycel` — affected >=0

## Details
Pycel through 1.0b30, when operating on an untrusted spreadsheet, allows code execution via a crafted formula in a cell, such as one beginning with the `=IF(A1=200, eval("__import__('os').system(` substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53924
- https://gist.github.com/aelmosalamy/cb098e61939718d2bb248fd1cc94f287
- https://github.com/dgorissen/pycel
- https://github.com/pypa/advisory-database/tree/main/vulns/pycel/PYSEC-2025-177.yaml
- https://github.com/stephenrauch/pycel
- https://pypi.org/project/pycel
