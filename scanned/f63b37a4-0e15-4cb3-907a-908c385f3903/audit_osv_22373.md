# [H] CVE-2022-27666

## Summary
Severity: High
Advisory: CVE-2022-27666
Aliases: A-227452856, PUB-A-227452856
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2022-27666
Type: osv

## Details
A heap buffer overflow flaw was found in IPsec ESP transformation code in net/ipv4/esp4.c and net/ipv6/esp6.c. This flaw allows a local attacker with a normal user privilege to overwrite kernel heap objects and may cause a local privilege escalation threat.

## References
- https://security.netapp.com/advisory/ntap-20220429-0001/
- https://www.debian.org/security/2022/dsa-5127
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=2061633
- https://github.com/torvalds/linux/commit/ebe48d368e97d007bfeb76fcb065d6cfc4c96645
