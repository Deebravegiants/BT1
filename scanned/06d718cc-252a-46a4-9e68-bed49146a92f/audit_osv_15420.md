# [H] CVE-2019-16159

## Summary
Severity: High
Advisory: CVE-2019-16159
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-16159
Type: osv

## Details
BIRD Internet Routing Daemon 1.6.x through 1.6.7 and 2.x through 2.0.5 has a stack-based buffer overflow. The BGP daemon's support for RFC 8203 administrative shutdown communication messages included an incorrect logical expression when checking the validity of an input message. Sending a shutdown communication with a sufficient message length causes a four-byte overflow to occur while processing the message, where two of the overflow bytes are attacker-controlled and two are fixed.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4F23NNAPXX65MGJQBPPTVGRV3T4XCKBV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MCVNQJBZYGGNAJNGOFEBE3IAJME2QIZB/
- http://bird.network.cz
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00065.html
- http://trubka.network.cz/pipermail/bird-users/2019-September/013718.html
- http://trubka.network.cz/pipermail/bird-users/2019-September/013720.html
- http://trubka.network.cz/pipermail/bird-users/2019-September/013722.html
- https://seclists.org/bugtraq/2019/Sep/34
- https://www.debian.org/security/2019/dsa-4528
- https://gitlab.labs.nic.cz/labs/bird/commit/1657c41c96b3c07d9265b07dd4912033ead4124b
- https://gitlab.labs.nic.cz/labs/bird/commit/8388f5a7e14108a1458fea35bfbb5a453e2c563c
