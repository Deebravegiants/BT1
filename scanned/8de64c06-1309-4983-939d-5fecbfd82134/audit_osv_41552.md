# [C] Apache Syncope: User self-service privilege escalation

## Summary
Severity: Critical
Advisory: CVE-2026-62183
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-62183
Type: osv

## Details
Improper Privilege Management vulnerability in Apache Syncope.

When:

* the all-Java user workflow adapter is configured, or
* the Flowable user workflow adapter is configured, bearing a BPMN definition not requiring admin approval for user self registration of self update requests

the following scenario could happen.
A REST API call can allow the user to grant themselves one or more of defined Roles, thus gaining their Entitlements and becoming in fact an administrator; the actual Entitlements gained depend on the Roles that are effectively defined on the specific Syncope deployment.


This issue affects Apache Syncope: from 3.0.0-M0 through 3.0.16, from 4.0.0-M0 Through 4.0.6, from 4.1.0-M0 through 4.1.1.

Users are recommended to upgrade to version 4.0.7 / 4.1.2, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/9
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62183.json
- https://lists.apache.org/thread/6r8cngvy43y2yk4jj3w060dt8vx0yzpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-62183
