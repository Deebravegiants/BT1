# [H] GitHub Security Lab (GHSL) Vulnerability Report: Arbitary write GHSL-2023-182 

## Summary
Severity: High
Advisory: GHSA-j8w6-2r9h-cxhj
CVE: CVE-2023-50731
CWE: CWE-22, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-j8w6-2r9h-cxhj
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=0 <23.11.4.1

## Details
### Impact

Issue: Arbitrary file write in file.py (GHSL-2023-183)

### Patches

Use mindsdb staging branch or v23.11.4.1

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-j8w6-2r9h-cxhj
- https://nvd.nist.gov/vuln/detail/CVE-2023-50731
- https://github.com/mindsdb/mindsdb
- https://github.com/mindsdb/mindsdb/blob/1821da719f34c022890c9ff25810218e71c5abbc/mindsdb/api/http/namespaces/file.py#L122-L125
- https://github.com/mindsdb/mindsdb/blob/1821da719f34c022890c9ff25810218e71c5abbc/mindsdb/api/http/namespaces/file.py#L138
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2023-279.yaml
- https://securitylab.github.com/advisories/GHSL-2023-182_GHSL-2023-184_mindsdb_mindsdb
