# [M] CVE-2019-25585

## Summary
Severity: Medium
Advisory: CVE-2019-25585
Aliases: PYSEC-2026-38
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-22
Source: https://osv.dev/vulnerability/CVE-2019-25585
Type: osv

## Details
Deluge 1.3.15 contains a denial of service vulnerability that allows local attackers to crash the application by supplying an excessively long string in the Webseeds field. Attackers can paste a buffer of 5000 bytes into the Webseeds field during torrent creation to trigger an application crash.

## References
- http://download.deluge-torrent.org/windows/deluge-1.3.15-win32-py2.7.exe
- https://dev.deluge-torrent.org/
- https://www.vulncheck.com/advisories/deluge-denial-of-service-via-webseeds-field
- https://www.exploit-db.com/exploits/46884
