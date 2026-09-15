# [H] ntlk unsafe deserialization vulnerability

## Summary
Severity: High
Advisory: GHSA-cgvx-9447-vcch
CVE: CVE-2024-39705
CWE: CWE-300, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-28
Source: https://github.com/advisories/GHSA-cgvx-9447-vcch
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.9

## Details
NLTK through 3.8.1 allows remote code execution if untrusted packages have pickled Python code, and the integrated data package download functionality is used. This affects, for example, averaged_perceptron_tagger and punkt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39705
- https://github.com/nltk/nltk/issues/2522
- https://github.com/nltk/nltk/issues/3266
- https://github.com/nltk/nltk/commit/441aecb7d33014bd08672232c6c8bb69c2ceaba2
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2024-167.yaml
- https://www.vicarius.io/vsociety/posts/rce-in-python-nltk-cve-2024-39705-39706
