# [H] Apache Ignite communicates to an external PHP server where sensitive information is sent

## Summary
Severity: High
Advisory: GHSA-8p83-68cw-943f
CVE: CVE-2017-7686
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-8p83-68cw-943f
Type: github-advisory

## Affected
- Maven: `org.apache.ignite:ignite-core` — affected >=0 <2.1

## Details
Apache Ignite 1.0.0-RC3 to 2.0 uses an update notifier component to update the users about new project releases that include additional functionality, bug fixes and performance improvements. To do that the component communicates to an external PHP server (http://ignite.run) where it needs to send some system properties like Apache Ignite or Java version. Some of the properties might contain user sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7686
- https://github.com/advisories/GHSA-8p83-68cw-943f
- http://apache-ignite-developers.2346864.n4.nabble.com/CVE-2017-7686-Apache-Ignite-Information-Disclosure-td19168.html
