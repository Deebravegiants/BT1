# [H] CVE-2021-46367

## Summary
Severity: High
Advisory: CVE-2021-46367
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-08
Source: https://osv.dev/vulnerability/CVE-2021-46367
Type: osv

## Details
RiteCMS version 3.1.0 and below suffers from a remote code execution vulnerability in the admin panel. An authenticated attacker can upload a PHP file and bypass the .htacess configuration to deny execution of .php files in media and files directory by default.

## References
- https://ritecms.com/
- https://gist.github.com/faisalfs10x/bd12e9abefb0d44f020bf297a14a4597
- https://packetstormsecurity.com/files/165430/RiteCMS-3.1.0-Shell-Upload-Remote-Code-Execution.html
- https://www.exploit-db.com/exploits/50616
