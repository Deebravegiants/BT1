# [H] Apache Syncope allows malicious administrators to inject Groovy code

## Summary
Severity: High
Advisory: GHSA-825g-mm5v-ggq4
CVE: CVE-2025-57738
CWE: CWE-653
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-825g-mm5v-ggq4
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.core:syncope-core-spring` — affected >=0 <3.0.14
- Maven: `org.apache.syncope.core:syncope-core-spring` — affected >=4.0.0-M0 <4.0.2

## Details
Apache Syncope offers the ability to extend / customize the base behavior on every deployment by allowing to provide custom implementations of a few Java interfaces; such implementations can be provided either as Java or Groovy classes, with the latter being particularly attractive as the machinery is set for runtime reload.
Such a feature has been available for a while, but recently it was discovered that a malicious administrator can inject Groovy code that can be executed remotely by a running Apache Syncope Core instance.
Users are recommended to upgrade to version 3.0.14 / 4.0.2, which fix this issue by forcing the Groovy code to run in a sandbox.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57738
- https://github.com/apache/syncope/commit/88c2b5b0be9e2ed66007d672e786165bc266e717
- https://github.com/apache/syncope/commit/8b08c4d5785599a0e38830dcff89738b93f02a16
- https://issues.apache.org/jira/browse/SYNCOPE-1907
- https://lists.apache.org/thread/x7cv6xv7z76y49grdr1hgj1pzw5zbby6
- https://syncope.apache.org/security#CVE-2025-57738
- http://github.com/apache/syncope
- http://www.openwall.com/lists/oss-security/2025/10/20/1
