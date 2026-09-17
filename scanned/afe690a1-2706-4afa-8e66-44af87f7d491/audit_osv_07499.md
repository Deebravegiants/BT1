# [H] BIT-sqlite-2021-36690

## Summary
Severity: High
Advisory: BIT-sqlite-2021-36690
Aliases: CVE-2021-36690
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2021-36690
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.36.0 <3.36.1

## Details
A segmentation fault can occur in the sqlite3.exe command-line component of SQLite 3.36.0 via the idxGetTableInfo function when there is a crafted SQL query. NOTE: the vendor disputes the relevance of this report because a sqlite3.exe user already has full privileges (e.g., is intentionally allowed to execute commands). This report does NOT imply any problem in the SQLite library.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/39
- http://seclists.org/fulldisclosure/2022/Oct/41
- http://seclists.org/fulldisclosure/2022/Oct/47
- http://seclists.org/fulldisclosure/2022/Oct/49
- https://support.apple.com/kb/HT213446
- https://support.apple.com/kb/HT213486
- https://support.apple.com/kb/HT213487
- https://support.apple.com/kb/HT213488
- https://www.sqlite.org/forum/forumpost/718c0a8d17
- https://nvd.nist.gov/vuln/detail/CVE-2021-36690
- https://lists.debian.org/debian-lts-announce/2024/09/msg00050.html
