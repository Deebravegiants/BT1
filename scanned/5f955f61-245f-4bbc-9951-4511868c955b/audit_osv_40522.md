# [C] Apache Syncope: Remote Code Execution via Scripted Connector

## Summary
Severity: Critical
Advisory: CVE-2026-53421
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-53421
Type: osv

## Details
Improper Isolation or Compartmentalization vulnerability in Apache Syncope.



An administrator with adequate entitlements can achieve remote code execution through the connector subsystem by relying on scripted connectors' (REST and SQL) capability to run Groovy scripts.

This issue affects Apache Syncope: from 3.0.0-M0 through 3.0.16, from 4.0.0-M0 Through 4.0.6, from 4.1.0-M0 through 4.1.1.




Users are recommended to upgrade to version 4.0.7 / 4.1.2, which fix this issue by hardening the Groovy security sandbox.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53421.json
- https://lists.apache.org/thread/nmzvz6gb2ldm30wvyk613r8dfrb6r8yx
- https://nvd.nist.gov/vuln/detail/CVE-2026-53421
