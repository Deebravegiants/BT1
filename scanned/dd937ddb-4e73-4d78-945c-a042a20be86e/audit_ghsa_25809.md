# [C] Improper Privilege Management in Open Web Analytics

## Summary
Severity: Critical
Advisory: GHSA-pr9q-v585-qv2w
CVE: CVE-2022-24637
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-19
Source: https://github.com/advisories/GHSA-pr9q-v585-qv2w
Type: github-advisory

## Affected
- Packagist: `open-web-analytics/open-web-analytics` — affected >=0 <1.7.4

## Details
Open Web Analytics (OWA) before 1.7.4 allows an unauthenticated remote attacker to obtain sensitive user information, which can be used to gain admin privileges by leveraging cache hashes. This occurs because files generated with '<?php (instead of the intended "<?php sequence) aren't handled by the PHP interpreter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24637
- https://devel0pment.de/?p=2494
- https://github.com/Open-Web-Analytics/Open-Web-Analytics
- https://github.com/Open-Web-Analytics/Open-Web-Analytics/releases/tag/1.7.4
- http://packetstormsecurity.com/files/169811/Open-Web-Analytics-1.7.3-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/171389/Open-Web-Analytics-1.7.3-Remote-Code-Execution.html
