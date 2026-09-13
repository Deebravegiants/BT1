# [C] CVE-2018-16975

## Summary
Severity: Critical
Advisory: CVE-2018-16975
Aliases: GHSA-x2w2-qgv6-8xrm
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-16975
Type: osv

## Details
An issue was discovered in Elefant CMS before 2.0.7. There is a PHP Code Execution Vulnerability in /designer/add/stylesheet.php by using a .php extension in the New Stylesheet Name field in conjunction with <?php content, because of insufficient input validation in apps/designer/handlers/csspreview.php.

## References
- https://github.com/jbroadway/elefant/releases/tag/elefant_2_0_7_stable
- https://github.com/jbroadway/elefant/commit/0795ab57c7ffa53ff4af57e229f6d9680fa54a21
- https://github.com/jbroadway/elefant/issues/286
