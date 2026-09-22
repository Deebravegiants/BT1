# [H] CVE-2019-14513

## Summary
Severity: High
Advisory: CVE-2019-14513
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-01
Source: https://osv.dev/vulnerability/CVE-2019-14513
Type: osv

## Details
Improper bounds checking in Dnsmasq before 2.76 allows an attacker controlled DNS server to send large DNS packets that result in a read operation beyond the buffer allocated for the packet, a different vulnerability than CVE-2017-14491.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00013.html
- https://github.com/Slovejoy/dnsmasq-pre2.76
