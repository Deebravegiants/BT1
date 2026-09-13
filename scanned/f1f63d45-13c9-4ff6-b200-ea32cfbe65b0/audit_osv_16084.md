# [M] CVE-2019-25632

## Summary
Severity: Medium
Advisory: CVE-2019-25632
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2019-25632
Type: osv

## Details
phpFileManager 1.7.8 contains a local file inclusion vulnerability that allows unauthenticated attackers to read arbitrary files by manipulating the action, fm_current_dir, and filename parameters. Attackers can send GET requests to index.php with crafted parameter values to access sensitive files like /etc/passwd from the server.

## References
- https://sourceforge.net/projects/phpfm/
- https://www.vulncheck.com/advisories/phpfilemanager-local-file-inclusion-via-index-php
- https://www.exploit-db.com/exploits/46638
