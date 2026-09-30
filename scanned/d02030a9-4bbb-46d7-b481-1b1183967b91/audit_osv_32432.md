# [H] Apache Kylin: The remote code execution via jdbc url

## Summary
Severity: High
Advisory: CVE-2025-30067
Aliases: GHSA-29m8-wh9p-5wc4
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-30067
Type: osv

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache Kylin. 
If an attacker gets access to Kylin's system or project admin permission, the JDBC connection configuration maybe altered to execute arbitrary code from the remote. You are fine as long as the Kylin's system and project admin access is well protected.

This issue affects Apache Kylin: from 4.0.0 through 5.0.1.

Users are recommended to upgrade to version 5.0.2 or above, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/03/27/4
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30067.json
- https://lists.apache.org/thread/6j19pt8yoqfphf1lprtrzoqkvz1gwbnc
- https://nvd.nist.gov/vuln/detail/CVE-2025-30067
