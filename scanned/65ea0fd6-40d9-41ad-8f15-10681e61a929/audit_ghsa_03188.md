# [M] Cross-site Scripting in OpenNMS Horizon

## Summary
Severity: Medium
Advisory: GHSA-jjhw-5mxp-2g2q
CVE: CVE-2021-25933
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-25
Source: https://github.com/advisories/GHSA-jjhw-5mxp-2g2q
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms` — affected >=1.0.0 <27.1.1

## Details
In OpenNMS Horizon, versions opennms-1-0-stable through opennms-27.1.1; OpenNMS Meridian, versions meridian-foundation-2015.1.0-1 through meridian-foundation-2019.1.18-1; meridian-foundation-2020.1.0-1 through meridian-foundation-2020.1.6-1 are vulnerable to Stored Cross-Site Scripting, since the function `validateFormInput()` performs improper validation checks on the input sent to the `groupName` and `groupComment` parameters. Due to this flaw, an authenticated attacker could inject arbitrary script and trick other admin users into downloading malicious files which can cause severe damage to the organization using opennms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25933
- https://github.com/OpenNMS/opennms/commit/8a97e6869d6e49da18b208c837438ace80049c01%2C
- https://github.com/OpenNMS/opennms/commit/8a97e6869d6e49da18b208c837438ace80049c01,
- https://github.com/OpenNMS/opennms/commit/eb08b5ed4c5548f3e941a1f0d0363ae4439fa98c
- https://github.com/OpenNMS/opennms/commit/f3ebfa3da5352b4d57f238b54c6db315ad99f10e
- https://github.com/OpenNMS/opennms
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25933
