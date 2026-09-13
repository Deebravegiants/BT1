# [M] TDengine Database Denial-of-Service

## Summary
Severity: Medium
Advisory: CVE-2023-38502
Aliases: GHSA-w23f-r2fm-27hf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-25
Source: https://osv.dev/vulnerability/CVE-2023-38502
Type: osv

## Details
TDengine is an open source, time-series database optimized for Internet of Things devices. Prior to version 3.0.7.1, TDengine DataBase crashes on UDF nested query. This issue affects TDengine Databases which let users connect and run arbitrary queries. Version 3.0.7.1 has a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38502.json
- https://github.com/taosdata/TDengine/security/advisories/GHSA-w23f-r2fm-27hf
- https://nvd.nist.gov/vuln/detail/CVE-2023-38502
