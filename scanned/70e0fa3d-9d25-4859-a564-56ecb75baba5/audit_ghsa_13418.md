# [H] Apache InLong Deserialization of Untrusted Data Vulnerability

## Summary
Severity: High
Advisory: GHSA-c3rh-f2w5-fghm
CVE: CVE-2023-31058
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-c3rh-f2w5-fghm
Type: github-advisory

## Affected
- Maven: `org.apache.inlong:manager-pojo` — affected >=1.4.0 <1.7.0
- Maven: `org.apache.inlong:manager-common` — affected >=1.4.0 <1.7.0

## Details
Deserialization of Untrusted Data Vulnerability in Apache Software Foundation Apache InLong.This issue affects Apache InLong: from 1.4.0 through 1.6.0. Attackers would bypass the `autoDeserialize` option filtering by adding blanks.  Users are advised to upgrade to Apache InLong's 1.7.0 or cherry-pick https://github.com/apache/inlong/pull/7674 to solve it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31058
- https://github.com/apache/inlong/pull/7674
- https://github.com/apache/inlong
- https://lists.apache.org/thread/bkcgbn9l61croxfyspf7xd42qb189s3z
