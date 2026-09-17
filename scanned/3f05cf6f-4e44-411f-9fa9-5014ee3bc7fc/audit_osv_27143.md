# [M] CVE-2024-11165

## Summary
Severity: Medium
Advisory: CVE-2024-11165
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:H/UI:N/VC:L/VI:H/VA:L/SC:L/SI:L/SA:L)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/CVE-2024-11165
Type: osv

## Details
An information disclosure vulnerability exists in the backup configuration process where the SAS token is not masked in the configuration response. This oversight results in sensitive information leakage within the yb_backup log files, exposing the SAS token in plaintext. The leakage occurs during the backup procedure, leading to potential unauthorized access to resources associated with the SAS token. This issue affects YugabyteDB Anywhere: from 2.20.0.0 before 2.20.7.0, from 2.23.0.0 before 2.23.1.0, from 2024.1.0.0 before 2024.1.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11165.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11165
- https://github.com/yugabyte/yugabyte-db/commit/920989b6c0db0222bb7a0cce46febc76cf72d438
