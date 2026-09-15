# [H] OpenNMS Horizon XXE Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-2qc8-r663-v864
CVE: CVE-2023-0871
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-2qc8-r663-v864
Type: github-advisory

## Affected
- Maven: `org.opennms.core:org.opennms.core.xml` — affected >=31.0.8 <32.0.2

## Details
XXE injection in `/rtc/post/ endpoint` in OpenNMS Horizon 31.0.8 and versions earlier than 32.0.2 on multiple platforms is vulnerable to XML external entity (XXE) injection, which can be used for instance to force Horizon to make arbitrary HTTP requests to internal and external services. The solution is to upgrade to Meridian 2023.1.6, 2022.1.19, 2021.1.30, 2020.1.38 or Horizon 32.0.2 or newer. Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0871
- https://github.com/OpenNMS/opennms/pull/6355
- https://github.com/OpenNMS/opennms/commit/5a3b0b62e0c612c9e2aa2c91c847abec71d767d5
- https://docs.opennms.com/horizon/32/releasenotes/changelog.html
- https://github.com/OpenNMS/opennms
