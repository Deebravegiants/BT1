# [H] Apache HttpClient disables domain checks

## Summary
Severity: High
Advisory: GHSA-73m2-qfq3-56cx
CVE: CVE-2025-27820
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-04-24
Source: https://github.com/advisories/GHSA-73m2-qfq3-56cx
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents.client5:httpclient5` — affected >=5.4-alpha1 <5.4.3

## Details
A bug in PSL validation logic in Apache HttpClient 5.4.x disables domain checks, affecting cookie management and host name verification. Discovered by the Apache HttpClient team. Fixed in the 5.4.3 release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27820
- https://github.com/apache/httpcomponents-client/pull/574
- https://github.com/apache/httpcomponents-client/pull/621
- https://github.com/apache/httpcomponents-client
- https://hc.apache.org/httpcomponents-client-5.4.x/index.html
- https://lists.apache.org/thread/55xhs40ncqv97qvoocok44995xp5kqn8
- https://security.netapp.com/advisory/ntap-20250516-0003
