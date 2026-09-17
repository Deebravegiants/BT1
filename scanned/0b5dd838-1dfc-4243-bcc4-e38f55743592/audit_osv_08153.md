# [M] CVE-2016-10728

## Summary
Severity: Medium
Advisory: CVE-2016-10728
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2016-10728
Type: osv

## Details
An issue was discovered in Suricata before 3.1.2. If an ICMPv4 error packet is received as the first packet on a flow in the to_client direction, it confuses the rule grouping lookup logic. The toclient inspection will then continue with the wrong rule group. This can lead to missed detection.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00019.html
- https://redmine.openinfosecfoundation.org/issues/1880
- https://suricata-ids.org/2016/09/07/suricata-3-1-2-released/
- https://github.com/kirillwow/ids_bypass
