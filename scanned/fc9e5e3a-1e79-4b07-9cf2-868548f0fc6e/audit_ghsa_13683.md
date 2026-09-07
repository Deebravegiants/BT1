# [M] OpenNMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c6xw-hg9q-3c9f
CVE: CVE-2023-40314
CWE: CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-c6xw-hg9q-3c9f
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms-webapp` — affected >=0 <32.0.5

## Details
Cross-site scripting in bootstrap.jsp in multiple versions of OpenNMS Meridian and Horizon allows an attacker access to confidential session information. The solution is to upgrade to Horizon 32.0.5 or newer and Meridian 2023.1.9 or newer.

Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40314
- https://github.com/OpenNMS/opennms/pull/6791
- https://github.com/OpenNMS/opennms
- https://opennms.atlassian.net/browse/NMS-15790
