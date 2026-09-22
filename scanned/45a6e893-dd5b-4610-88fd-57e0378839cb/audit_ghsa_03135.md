# [H] SQL Injection in librenms

## Summary
Severity: High
Advisory: GHSA-h59f-p56g-g75v
CVE: CVE-2020-35700
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-h59f-p56g-g75v
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <21.1.0

## Details
A second-order SQL injection issue in Widgets/TopDevicesController.php (aka the Top Devices dashboard widget) of LibreNMS before 21.1.0 allows remote authenticated attackers to execute arbitrary SQL commands via the sort_order parameter against the /ajax/form/widget-settings endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35700
- https://github.com/librenms/librenms/issues/12405
- https://github.com/librenms/librenms/pull/12422
- https://github.com/librenms/librenms/blob/master/app/Http/Controllers/Widgets/TopDevicesController.php
- https://github.com/librenms/librenms/releases/tag/21.1.0
- https://www.horizon3.ai/disclosures/librenms-second-order-sqli
