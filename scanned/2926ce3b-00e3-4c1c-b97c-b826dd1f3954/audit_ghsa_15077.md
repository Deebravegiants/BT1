# [C] Arbitrary Code Execution in Pillow

## Summary
Severity: Critical
Advisory: GHSA-3f63-hfp8-52jq
CVE: CVE-2023-50447
CWE: CWE-94, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-3f63-hfp8-52jq
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=0 <10.2.0

## Details
Pillow through 10.1.0 allows PIL.ImageMath.eval Arbitrary Code Execution via the environment parameter, a different vulnerability than CVE-2022-22817 (which was about the expression parameter).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50447
- https://github.com/python-pillow/Pillow/commit/45c726fd4daa63236a8f3653530f297dc87b160a
- https://devhub.checkmarx.com/cve-details/CVE-2023-50447
- https://duartecsantos.github.io/2023-01-02-CVE-2023-50447
- https://duartecsantos.github.io/2024-01-02-CVE-2023-50447
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases
- https://lists.debian.org/debian-lts-announce/2024/01/msg00019.html
- https://pillow.readthedocs.io/en/stable/releasenotes/10.2.0.html#security
- http://www.openwall.com/lists/oss-security/2024/01/20/1
