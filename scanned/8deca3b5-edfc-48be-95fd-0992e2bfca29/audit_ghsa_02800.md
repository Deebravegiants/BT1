# [H] Directory traversal in mkdocs

## Summary
Severity: High
Advisory: GHSA-qh9q-34h6-hcv9
CVE: CVE-2021-40978
CWE: CWE-12, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-qh9q-34h6-hcv9
Type: github-advisory

## Affected
- PyPI: `mkdocs` — affected >=1.2.2 <1.2.3

## Details
The mkdocs 1.2.2 built-in dev-server allows directory traversal using the port 8000, enabling remote exploitation to obtain :sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40978
- https://github.com/mkdocs/mkdocs/issues/2601
- https://github.com/nisdn/CVE-2021-40978/issues/1
- https://github.com/mkdocs/mkdocs/pull/2604
- https://github.com/mkdocs/mkdocs/commit/1b15412f4caae476c262210315fd068d0521a833
- https://github.com/mkdocs/mkdocs/commit/57540911a0d632674dd23edec765189f96f84f6b
- https://github.com/mkdocs/mkdocs
- https://github.com/mkdocs/mkdocs/releases/tag/1.2.3
- https://github.com/nisdn/CVE-2021-40978
- https://github.com/pypa/advisory-database/tree/main/vulns/mkdocs/PYSEC-2021-878.yaml
