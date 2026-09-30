# [H] OpenNMS Horizon RCE via JEXL2 expression

## Summary
Severity: High
Advisory: GHSA-c3mp-9vx3-2rvv
CVE: CVE-2021-3396
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c3mp-9vx3-2rvv
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms` — affected >=16.0.0 <27.0.4
- Maven: `org.opennms.features:org.opennms.features.measurements` — affected >=16.0.0 <27.0.4
- Maven: `org.opennms:opennms-provision` — affected >=16.0.0 <27.0.4
- Maven: `org.opennms:opennms-util` — affected >=16.0.0 <27.0.4

## Details
OpenNMS Meridian 2016, 2017, 2018 before 2018.1.25, 2019 before 2019.1.16, and 2020 before 2020.1.5, Horizon 1.2 through 27.0.4, and Newts <1.5.3 has Incorrect Access Control, which allows local and remote code execution using JEXL expressions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3396
- https://github.com/OpenNMS/opennms/pull/3281
- https://issues.opennms.org/browse/NMS-13103
- https://www.opennms.com/en/blog/2021-02-16-cve-2021-3396-full-security-disclosure
