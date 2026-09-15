# [C] CVE-2019-16124

## Summary
Severity: Critical
Advisory: CVE-2019-16124
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-16124
Type: osv

## Details
In YouPHPTube 7.4, the file install/checkConfiguration.php has no access control, which leads to everyone being able to edit the configuration file, and insert malicious PHP code.

## References
- https://zerodays.lol/
- https://github.com/YouPHPTube/YouPHPTube/commit/b32b410c9191c3c5db888514c29d7921f124d883
- https://www.exploit-db.com/exploits/47326
