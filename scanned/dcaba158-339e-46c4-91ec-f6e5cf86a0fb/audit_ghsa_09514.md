# [H] Apache Syncope has an Improper Isolation or Compartmentalization vulnerability

## Summary
Severity: High
Advisory: GHSA-gq7g-vg2q-jvq3
CVE: CVE-2026-42782
CWE: CWE-653
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-gq7g-vg2q-jvq3
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.core:syncope-core-spring` — affected >=3.0.0-M0
- Maven: `org.apache.syncope.core:syncope-core-spring` — affected >=4.0.0-M0 <4.0.6
- Maven: `org.apache.syncope.core:syncope-core-spring` — affected >=4.1.0-M0 <4.1.1

## Details
Improper Isolation or Compartmentalization vulnerability in Apache Syncope.

An administrator with adequate entitlements for Implementations can create a malicious Groovy class containing untrusted code reaching a non-sandboxed execution path via the class static initializer.

This issue affects Apache Syncope: 3.0 through 3.0.16, 4.0 through 4.0.5, 4.1.0.

Users are recommended to upgrade to version 4.0.6 / 4.1.1, which fix this issue by forcing even the static initializer in Groovy code to run in a sandbox.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42782
- https://lists.apache.org/thread/b869ms0ofrd129f7tgsn9flxgv9ztg2r
- http://www.openwall.com/lists/oss-security/2026/05/25/4
