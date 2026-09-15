# [H] Infinite Loop in Pygments

## Summary
Severity: High
Advisory: GHSA-9w8r-397f-prfh
CVE: CVE-2021-20270
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-9w8r-397f-prfh
Type: github-advisory

## Affected
- PyPI: `Pygments` — affected >=1.5 <2.7.4

## Details
An infinite loop in SMLLexer in Pygments versions 1.5 to 2.7.3 may lead to denial of service when performing syntax highlighting of a Standard ML (SML) source file, as demonstrated by input that only contains the "exception" keyword.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20270
- https://github.com/pygments/pygments/commit/f91804ff4772e3ab41f46e28d370f57898700333
- https://bugzilla.redhat.com/show_bug.cgi?id=1922136
- https://github.com/pygments/pygments
- https://github.com/pypa/advisory-database/tree/main/vulns/pygments/PYSEC-2021-140.yaml
- https://lists.debian.org/debian-lts-announce/2021/05/msg00003.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00006.html
- https://www.debian.org/security/2021/dsa-4889
- https://www.oracle.com/security-alerts/cpuoct2021.html
