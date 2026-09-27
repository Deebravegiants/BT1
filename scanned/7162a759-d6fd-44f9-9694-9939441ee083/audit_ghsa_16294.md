# [H] Improper Certificate Validation in Apache DolphinScheduler

## Summary
Severity: High
Advisory: GHSA-37gx-jqx9-fwmg
CVE: CVE-2023-49250
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-37gx-jqx9-fwmg
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <3.2.1

## Details
Because the HttpUtils class did not verify certificates, an attacker that could perform a Man-in-the-Middle (MITM) attack on outgoing https connections could impersonate the server.

This issue affects Apache DolphinScheduler: before 3.2.1.

Users are recommended to upgrade to version 3.2.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49250
- https://github.com/apache/dolphinscheduler/pull/15288
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/wgs2jvhbmq8xnd6rmg0ymz73nyj7b3qn
- http://www.openwall.com/lists/oss-security/2024/02/20/1
