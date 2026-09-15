# [C] CVE-2021-44847

## Summary
Severity: Critical
Advisory: CVE-2021-44847
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-13
Source: https://osv.dev/vulnerability/CVE-2021-44847
Type: osv

## Details
A stack-based buffer overflow in handle_request function in DHT.c in toxcore 0.1.9 through 0.1.11 and 0.2.0 through 0.2.12 (caused by an improper length calculation during the handling of received network packets) allows remote attackers to crash the process or potentially execute arbitrary code via a network packet.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S7EBS3NIRYJ7V3PTNINP3PJSVUHGZTGA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLTKINSPO5T65LB3ZASDPCREKUE22RYE/
- https://github.com/TokTok/c-toxcore/pull/1718
