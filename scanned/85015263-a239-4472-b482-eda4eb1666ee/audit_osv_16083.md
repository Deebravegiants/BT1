# [M] CVE-2019-25586

## Summary
Severity: Medium
Advisory: CVE-2019-25586
Aliases: PYSEC-2026-39
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-22
Source: https://osv.dev/vulnerability/CVE-2019-25586
Type: osv

## Details
Deluge 1.3.15 contains a denial of service vulnerability that allows local attackers to crash the application by supplying an excessively long string in the URL field. Attackers can paste a buffer of 5000 characters into the 'From URL' field during torrent addition to trigger an application crash.

## References
- http://download.deluge-torrent.org/windows/deluge-1.3.15-win32-py2.7.exe
- https://dev.deluge-torrent.org/
- https://www.vulncheck.com/advisories/deluge-denial-of-service-via-url-field
- https://www.exploit-db.com/exploits/46883
