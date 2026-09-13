# [M] BIT-nifi-2020-1928

## Summary
Severity: Medium
Advisory: BIT-nifi-2020-1928
Aliases: CVE-2020-1928, GHSA-w4fj-ccr6-7pcp
Ecosystem: Bitnami
Published: 2025-09-12
Source: https://osv.dev/vulnerability/BIT-nifi-2020-1928
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.10.0

## Details
An information disclosure vulnerability was found in Apache NiFi 1.10.0. The sensitive parameter parser would log parsed values for debugging purposes. This would expose literal values entered in a sensitive property when no parameter was present.

## References
- https://lists.apache.org/thread.html/r17aaa3a05b5b7fe9075613dd0c681efa60a4f8c8fbad152c61371b6e%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r38a5b7943b9a62ecb853acc22ef08ff586a7b3c66e08f949f0396ab1%40%3Cusers.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rd50baccd1bbb96c2327d5a8caa25a49692b3d68d96915bd1cfbb9f8b%40%3Cusers.tomcat.apache.org%3E
- https://nifi.apache.org/security.html#CVE-2020-1928
- https://nvd.nist.gov/vuln/detail/CVE-2020-1928
