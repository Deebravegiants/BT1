# [H] OpenNMS vulnerable to remote code execution

## Summary
Severity: High
Advisory: GHSA-5m5f-qg8r-p9qf
CVE: CVE-2023-40313
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-08-17
Source: https://github.com/advisories/GHSA-5m5f-qg8r-p9qf
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms-base-assembly` — affected >=0 <32.0.2

## Details
A BeanShell interpreter in remote server mode runs in OpenNMS Horizon versions earlier than 32.0.2 and in related Meridian versions which could allow arbitrary remote Java code execution. The solution is to upgrade to Meridian 2023.1.6, 2022.1.19, 2021.1.30, 2020.1.38 or Horizon 32.0.2 or newer. Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40313
- https://github.com/OpenNMS/opennms/pull/6368
- https://github.com/OpenNMS/opennms/commit/2909448b039bd46241efa52c450ffdb4f5a7dee1
- https://docs.opennms.com/horizon/32/releasenotes/changelog.html
- https://github.com/OpenNMS/opennms
