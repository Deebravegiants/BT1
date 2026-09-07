# [H] Improper Encoding or Escaping of Output in Apache Superset

## Summary
Severity: High
Advisory: GHSA-5fp8-c45m-256p
CVE: CVE-2021-42250
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5fp8-c45m-256p
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <1.3.2

## Details
Improper output neutralization for Logs. A specific Apache Superset HTTP endpoint allowed for an authenticated user to forge log entries or inject malicious content into logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42250
- https://github.com/advisories/GHSA-5fp8-c45m-256p
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2021-435.yaml
- https://lists.apache.org/thread/53lkszw6d3tybp5t99nvgcj538b9trw9
- http://www.openwall.com/lists/oss-security/2021/11/17/2
