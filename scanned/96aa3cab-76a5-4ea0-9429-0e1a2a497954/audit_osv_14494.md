# [H] CVE-2019-10055

## Summary
Severity: High
Advisory: CVE-2019-10055
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-28
Source: https://osv.dev/vulnerability/CVE-2019-10055
Type: osv

## Details
An issue was discovered in Suricata 4.1.3. The function ftp_pasv_response lacks a check for the length of part1 and part2, leading to a crash within the ftp/mod.rs file.

## References
- https://suricata-ids.org/2019/04/30/suricata-4-1-4-released/
- https://redmine.openinfosecfoundation.org/issues/2949
