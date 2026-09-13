# [C] Apache Syncope: RCE via Groovy Sandbox bypass

## Summary
Severity: Critical
Advisory: CVE-2026-63071
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63071
Type: osv

## Details
Improper Isolation or Compartmentalization vulnerability in Apache Syncope.

An administrator with adequate entitlements for Implementations can create a malicious Groovy class containing untrusted code bypassing the Groovy security sandbox.

This issue affects Apache Syncope: from 3.0.0-M0 through 3.0.16, from 4.0.0-M0 through 4.0.6, from 4.1.0-M0 through 4.1.1.

Users are recommended to upgrade to version 4.0.7 / 4.1.2, which fix this issue by tightening the Groovy security sandbox.

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/11
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63071.json
- https://lists.apache.org/thread/2236mlm6hbvs6g16yqz5y9s8bb7q1lo1
- https://nvd.nist.gov/vuln/detail/CVE-2026-63071
