# [M] OpenNMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-qfw7-pfxx-h9q2
CVE: CVE-2023-40311
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-08-14
Source: https://github.com/advisories/GHSA-qfw7-pfxx-h9q2
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms-webapp` — affected >=31.0.8 <32.0.2

## Details
Multiple stored XSS were found on different JSP files with unsanitized parameters in OpenMNS Horizon 31.0.8 and versions earlier than 32.0.2 on multiple platforms that allow an attacker to store on database and then load on JSPs or Angular templates. The solution is to upgrade to Meridian 2023.1.6, 2022.1.19, 2021.1.30, 2020.1.38 or Horizon 32.0.2 or newer. Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet. OpenNMS thanks Jordi Miralles Comins for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40311
- https://github.com/OpenNMS/opennms/pull/6365
- https://github.com/OpenNMS/opennms/pull/6366
- https://github.com/OpenNMS/opennms/commit/6ccc5de1a23d440560e0f09dfd94f8392c21e70d
- https://github.com/OpenNMS/opennms/commit/c67d1cae2fa1fb806c9d422f6e6fbf4ebfde6b60
- https://github.com/OpenNMS/opennms
