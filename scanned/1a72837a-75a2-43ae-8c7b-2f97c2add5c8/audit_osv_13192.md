# [H] CVE-2018-18541

## Summary
Severity: High
Advisory: CVE-2018-18541
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-20
Source: https://osv.dev/vulnerability/CVE-2018-18541
Type: osv

## Details
In Teeworlds before 0.6.5, connection packets could be forged. There was no challenge-response involved in the connection build up. A remote attacker could send connection packets from a spoofed IP address and occupy all server slots, or even use them for a reflection attack using map download packets.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00077.html
- https://teeworlds.com/?page=news&id=12544
- https://www.debian.org/security/2018/dsa-4329
- https://bugs.debian.org/911487
- https://github.com/teeworlds/teeworlds/issues/1536
