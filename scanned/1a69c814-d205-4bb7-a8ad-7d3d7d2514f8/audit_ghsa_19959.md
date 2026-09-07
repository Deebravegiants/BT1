# [C] py7zr directory traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-m8xw-9x5x-6vh3
CVE: CVE-2022-44900
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-06
Source: https://github.com/advisories/GHSA-m8xw-9x5x-6vh3
Type: github-advisory

## Affected
- PyPI: `py7zr` — affected >=0 <0.20.1

## Details
A directory traversal vulnerability in the SevenZipFile.extractall() function of the python library py7zr v0.20.0 and earlier allows attackers to write arbitrary files via extracting a crafted 7z file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44900
- https://github.com/miurahr/py7zr/commit/1bb43f17515c7f69673a1c88ab9cc72a7bbef406
- https://advisory-inbox.githubapp.com/advisory_reviews/GHSA-m8xw-9x5x-6vh3
- https://github.com/miurahr/py7zr
- https://github.com/pypa/advisory-database/tree/main/vulns/py7zr/PYSEC-2022-42998.yaml
- https://lessonsec.com/cve/cve-2022-44900
- http://packetstormsecurity.com/files/170127/py7zr-0.20.0-Directory-Traversal.html
