# [M] ReDoS in Embedchain

## Summary
Severity: Medium
Advisory: GHSA-r67w-f99w-mgxj
CVE: CVE-2024-23732
CWE: CWE-1333
Ecosystem: PyPI
Published: 2024-01-21
Source: https://github.com/advisories/GHSA-r67w-f99w-mgxj
Type: github-advisory

## Affected
- PyPI: `embedchain` — affected >=0 <0.1.57

## Details
The JSON loader in Embedchain before 0.1.57 allows a ReDoS (regular expression denial of service) via a long string to json.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23732
- https://github.com/embedchain/embedchain/pull/1122
- https://github.com/embedchain/embedchain/compare/0.1.56...0.1.57
- https://github.com/pypa/advisory-database/tree/main/vulns/embedchain/PYSEC-2024-8.yaml
