# [M] Improper Restriction of XML External Entity References in AWS Advanced JDBC Wrapper RemoteQueryCachePlugin

## Summary
Severity: Medium
Advisory: CVE-2026-18061
Aliases: GHSA-fpvp-qwgm-v6h9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-18061
Type: osv

## Details
Improper restriction of XML external entity references in the RemoteQueryCachePlugin in AWS Advanced JDBC Wrapper 3.3.0 through 4.2.0 might allow an actor with write access to the shared cache infrastructure to disclose sensitive files from application hosts that read cached query results, including stored database and IAM role credentials, via crafted XML data in a cached column value.



To remediate this issue, users should upgrade to version 4.3.0 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-109-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18061.json
- https://github.com/aws/aws-advanced-jdbc-wrapper/releases/tag/4.3.0
- https://github.com/aws/aws-advanced-jdbc-wrapper/security/advisories/GHSA-fpvp-qwgm-v6h9
- https://nvd.nist.gov/vuln/detail/CVE-2026-18061
