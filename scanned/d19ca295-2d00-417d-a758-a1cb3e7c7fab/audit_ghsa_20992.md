# [H] Apache Geode versions deserialization of untrusted datawhen using JMX over RMI on Java 11

## Summary
Severity: High
Advisory: GHSA-qf8g-vpwp-6579
CVE: CVE-2022-37022
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-01
Source: https://github.com/advisories/GHSA-qf8g-vpwp-6579
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=0 <1.15.0

## Details
Apache Geode versions up to 1.12.2 and 1.13.2 are vulnerable to a deserialization of untrusted data flaw when using JMX over RMI on Java 11. Any user wishing to protect against deserialization attacks involving JMX or RMI should upgrade to Apache Geode 1.15. Use of 1.15 on Java 11 will automatically protect JMX over RMI against deserialization attacks. This should have no impact on performance since it only affects JMX/RMI which Gfsh uses to communicate with the JMX Manager which is hosted on a Locator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37022
- https://lists.apache.org/thread/kr1y4l9752g1ww1shnmh8dbfjq785k4m
