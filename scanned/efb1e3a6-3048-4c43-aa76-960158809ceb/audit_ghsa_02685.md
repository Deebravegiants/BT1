# [H] Infinite Loop in rencode

## Summary
Severity: High
Advisory: GHSA-gh8j-2pgf-x458
CVE: CVE-2021-40839
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-13
Source: https://github.com/advisories/GHSA-gh8j-2pgf-x458
Type: github-advisory

## Affected
- PyPI: `rencode` — affected >=0

## Details
The rencode package through 1.0.6 for Python allows an infinite loop in typecode decoding (such as via ;\x2f\x7f), enabling a remote attack that consumes CPU and memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40839
- https://github.com/aresch/rencode/pull/29
- https://github.com/aresch/rencode/commit/572ff74586d9b1daab904c6f7f7009ce0143bb75
- https://github.com/advisories/GHSA-gh8j-2pgf-x458
- https://github.com/aresch/rencode
- https://github.com/pypa/advisory-database/tree/main/vulns/rencode/PYSEC-2021-345.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BMVQRPDVSVZNGGX57CFKCYT3DEYO4QB6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MCLETLGVM5DBX6QNHQFW6TWGO5T3DENY
- https://pypi.org/project/rencode/#history
- https://seclists.org/fulldisclosure/2021/Sep/16
- https://security.netapp.com/advisory/ntap-20211008-0001
