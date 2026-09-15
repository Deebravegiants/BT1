# [M] S3Scanner allows Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-qppg-v75c-r5ff
CVE: CVE-2021-32061
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-11-30
Source: https://github.com/advisories/GHSA-qppg-v75c-r5ff
Type: github-advisory

## Affected
- PyPI: `s3scanner` — affected >=0 <2.0.2

## Details
S3Scanner before 2.0.2 allows Directory Traversal via a crafted bucket, as demonstrated by a `<Key>../` substring in a `ListBucketResult` element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32061
- https://github.com/sa7mon/S3Scanner/issues/122
- https://github.com/sa7mon/S3Scanner/commit/fafa30a3bd35b496b3f7db9bfc35b75a8a06bcd1
- https://github.com/advisories/GHSA-qppg-v75c-r5ff
- https://github.com/pypa/advisory-database/tree/main/vulns/s3scanner/PYSEC-2021-433.yaml
- https://github.com/sa7mon/S3Scanner
- https://github.com/sa7mon/S3Scanner/releases/tag/2.0.2
- https://vuln.ryotak.me/advisories/62
