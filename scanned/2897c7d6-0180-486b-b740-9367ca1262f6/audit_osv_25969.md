# [C] iTop limit pages/exec.php script to PHP files

## Summary
Severity: Critical
Advisory: CVE-2023-48710
Aliases: GHSA-g652-q7cc-7hfc
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-15
Source: https://osv.dev/vulnerability/CVE-2023-48710
Type: osv

## Details
iTop is an IT service management platform.  Files from the `env-production` folder can be retrieved even though they should have restricted access.  Hopefully, there is no sensitive files stored in that folder natively, but there could be from a third-party module. 
 The `pages/exec.php` script as been fixed to limit execution of PHP files only.  Other file types won't be retrieved and exposed.  The vulnerability is fixed in 2.7.10, 3.0.4, 3.1.1, and 3.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48710.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-g652-q7cc-7hfc
- https://nvd.nist.gov/vuln/detail/CVE-2023-48710
- https://github.com/Combodo/iTop/commit/3b2da39469f7a4636ed250ed0d33f4efff38be26
