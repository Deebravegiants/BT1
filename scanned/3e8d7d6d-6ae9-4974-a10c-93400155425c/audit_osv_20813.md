# [H] CVE-2021-37367

## Summary
Severity: High
Advisory: CVE-2021-37367
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2021-37367
Type: osv

## Details
CTparental before 4.45.07 is affected by a code execution vulnerability in the CTparental admin panel. Because The file "bl_categories_help.php" is vulnerable to directory traversal, an attacker can create a file that contains scripts and run arbitrary commands.

## References
- https://gist.github.com/securylight/092ba96a660e07ad76f2a380c2eaa75a
- https://gitlab.com/marsat/CTparental/
