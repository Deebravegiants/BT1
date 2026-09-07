# [M] LibreNMS XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9m82-f3wx-p625
CVE: CVE-2018-18478
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9m82-f3wx-p625
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.44

## Details
Persistent Cross-Site Scripting (XSS) issues in LibreNMS before 1.44 allow remote attackers to inject arbitrary web script or HTML via the dashboard_name parameter in the /ajax_form.php resource, related to html/includes/forms/add-dashboard.inc.php, html/includes/forms/delete-dashboard.inc.php, and html/includes/forms/edit-dashboard.inc.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18478
- https://github.com/librenms/librenms/issues/9170
- https://github.com/librenms/librenms/pull/9171
- https://github.com/librenms/librenms/releases/tag/1.44
- https://hackpuntes.com/cve-2018-18478-libre-nms-1-43-cross-site-scripting-persistente
