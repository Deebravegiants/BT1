# [C] CVE-2021-40889

## Summary
Severity: Critical
Advisory: CVE-2021-40889
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-40889
Type: osv

## Details
CMSUno version 1.7.2 is affected by a PHP code execution vulnerability. sauvePass action in {webroot}/uno/central.php file calls to file_put_contents() function to write username in password.php file when a user successfully changed their password. The attacker can inject malicious PHP code into password.php and then use the login function to execute code.

## References
- https://github.com/boiteasite/cmsuno/issues/19
