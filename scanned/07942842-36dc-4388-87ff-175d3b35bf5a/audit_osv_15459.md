# [C] CVE-2019-16410

## Summary
Severity: Critical
Advisory: CVE-2019-16410
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/CVE-2019-16410
Type: osv

## Details
An issue was discovered in Suricata 4.1.4. By sending multiple fragmented IPv4 packets, the function Defrag4Reassemble in defrag.c tries to access a memory region that is not allocated, because of a lack of header_len checking.

## References
- https://www.code-intelligence.com/cve-2019-16410
- https://lists.openinfosecfoundation.org/pipermail/oisf-announce/
- https://suricata-ids.org/2019/09/24/suricata-4-1-5-released/
