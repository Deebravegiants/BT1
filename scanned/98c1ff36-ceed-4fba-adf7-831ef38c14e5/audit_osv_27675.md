# [C] CVE-2024-24724

## Summary
Severity: Critical
Advisory: CVE-2024-24724
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-24724
Type: osv

## Details
Gibbon through 26.0.00 allows /modules/School%20Admin/messengerSettings.php Server Side Template Injection leading to Remote Code Execution because input is passed to the Twig template engine (messengerSettings.php) without sanitization.

## References
- https://gibbonedu.org/download/
- https://packetstormsecurity.com/files/177857
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24724.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24724
