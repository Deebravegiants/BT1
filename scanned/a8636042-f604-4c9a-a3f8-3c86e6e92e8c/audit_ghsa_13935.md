# [M] OpenNMS has potential Insertion of Sensitive Information into Log File vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9xpj-mvp2-3943
CVE: CVE-2023-0815
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-9xpj-mvp2-3943
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms` — affected >=0 <31.0.4

## Details
Potential Insertion of Sensitive Information into Jetty Log Files in multiple versions of OpenNMS Meridian and Horizon could allow disclosure of usernames and passwords if the logging level is set to debug.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0815
- https://github.com/OpenNMS/opennms/pull/5741/files
- https://docs.opennms.com/meridian/2022/releasenotes/changelog.html#releasenotes-changelog-Meridian-2022.1.13
- https://github.com/OpenNMS/opennms
- https://github.com/OpenNMS/opennms/releases/tag/opennms-31.0.4-1
