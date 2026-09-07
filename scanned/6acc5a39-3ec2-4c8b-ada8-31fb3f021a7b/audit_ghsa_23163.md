# [M] phpBB Server side request forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-4hx9-p925-qcv7
CVE: CVE-2019-11767
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4hx9-p925-qcv7
Type: github-advisory

## Affected
- Packagist: `phpbb/phpbb` — affected >=0 <3.2.6

## Details
Server side request forgery (SSRF) in phpBB before 3.2.6 allows checking for the existence of files and services on the local network of the host through the remote avatar upload function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11767
- https://github.com/phpbb/phpbb-app
- https://www.phpbb.com/community/viewtopic.php?f=14&t=2509941
