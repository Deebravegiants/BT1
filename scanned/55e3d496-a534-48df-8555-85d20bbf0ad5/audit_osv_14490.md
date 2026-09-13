# [H] CVE-2019-10051

## Summary
Severity: High
Advisory: CVE-2019-10051
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-28
Source: https://osv.dev/vulnerability/CVE-2019-10051
Type: osv

## Details
An issue was discovered in Suricata 4.1.3. If the function filetracker_newchunk encounters an unsafe "Some(sfcm) => { ft.new_chunk }" item, then the program enters an smb/files.rs error condition and crashes.

## References
- https://suricata-ids.org/2019/04/30/suricata-4-1-4-released/
- https://redmine.openinfosecfoundation.org/issues/2896
- https://github.com/OISF/suricata/pull/3734
