# [M] Pekko Management may not properly apply authenticator when Basic Authentication is enabled

## Summary
Severity: Medium
Advisory: GHSA-9qvj-rpj8-v5c8
CVE: CVE-2025-46548
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-03
Source: https://github.com/advisories/GHSA-9qvj-rpj8-v5c8
Type: github-advisory

## Affected
- Maven: `org.apache.pekko:pekko-management_2.12` — affected >=0 <1.1.1
- Maven: `com.lightbend.akka.management:akka-management_2.13` — affected >=0 <1.6.1
- Maven: `org.apache.pekko:pekko-management_2.13` — affected >=0 <1.1.1
- Maven: `org.apache.pekko:pekko-management_3` — affected >=0 <1.1.1
- Maven: `com.lightbend.akka.management:akka-management_2.12` — affected >=0 <1.6.1
- Maven: `com.lightbend.akka.management:akka-management_3` — affected >=0 <1.6.1

## Details
If you enable Basic Authentication in Pekko Management using the Java DSL, the authenticator may not be properly applied.


Users that rely on authentication instead of making sure the Management API ports are only available to trusted users are recommended to upgrade to version 1.1.1, which fixes this issue. Akka was affected by the same issue and has released the fix in version 1.6.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-46548
- https://github.com/akka/akka-management/pull/1385
- https://github.com/apache/pekko-management/pull/418
- https://lists.apache.org/thread/tnd84hj9w0ggjcft6cp12q67d5jzhp66
- http://www.openwall.com/lists/oss-security/2025/06/03/7
