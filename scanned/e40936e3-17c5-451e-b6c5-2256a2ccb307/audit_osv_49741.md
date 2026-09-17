# [M] CVE-2019-18282

## Summary
Severity: Medium
Advisory: CVE-2019-18282
Aliases: A-148588557, ASB-A-148588557
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-01-16
Source: https://osv.dev/vulnerability/CVE-2019-18282
Type: osv

## Details
The flow_dissector feature in the Linux kernel 4.3 through 5.x before 5.3.10 has a device tracking vulnerability, aka CID-55667441c84f. This occurs because the auto flowlabel of a UDP IPv6 packet relies on a 32-bit hashrnd value as a secret, and because jhash (instead of siphash) is used. The hashrnd value remains the same starting from boot time, and can be inferred by an attacker. This affects net/core/flow_dissector.c and related code.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.10
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20200204-0002/
- https://www.computer.org/csdl/proceedings-article/sp/2020/349700b594/1j2LgrHDR2o
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=55667441c84fa5e0911a0aac44fb059c15ba6da2
