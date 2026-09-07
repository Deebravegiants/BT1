# [M] Cross-Site Request Forgery in OpenNMS Horizon

## Summary
Severity: Medium
Advisory: GHSA-p63h-7hw8-5cw4
CVE: CVE-2021-25930
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-05-25
Source: https://github.com/advisories/GHSA-p63h-7hw8-5cw4
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms` — affected >=1.0.0 <27.1.1
- Maven: `org.opennms:opennms-config` — affected >=1.0.0 <27.1.1

## Details
In OpenNMS Horizon, versions opennms-1-0-stable through opennms-27.1.1; OpenNMS Meridian, versions meridian-foundation-2015.1.0-1 through meridian-foundation-2019.1.18-1; meridian-foundation-2020.1.0-1 through meridian-foundation-2020.1.6-1 are vulnerable to CSRF, due to no CSRF protection, and since there is no validation of an existing user name while renaming a user. As a result, privileges of the renamed user are being overwritten by the old user and the old user is being deleted from the user list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25930
- https://github.com/OpenNMS/opennms/commit/607151ea8f90212a3fb37c977fa57c7d58d26a84
- https://github.com/OpenNMS/opennms/commit/eb08b5ed4c5548f3e941a1f0d0363ae4439fa98c
- https://github.com/OpenNMS/opennms
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25930
