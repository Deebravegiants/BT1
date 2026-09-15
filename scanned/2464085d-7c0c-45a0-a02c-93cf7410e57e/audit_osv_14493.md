# [H] CVE-2019-10054

## Summary
Severity: High
Advisory: CVE-2019-10054
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-28
Source: https://osv.dev/vulnerability/CVE-2019-10054
Type: osv

## Details
An issue was discovered in Suricata 4.1.3. The function process_reply_record_v3 lacks a check for the length of reply.data. It causes an invalid memory access and the program crashes within the nfs/nfs3.rs file.

## References
- https://suricata-ids.org/2019/04/30/suricata-4-1-4-released/
- https://redmine.openinfosecfoundation.org/issues/2943
