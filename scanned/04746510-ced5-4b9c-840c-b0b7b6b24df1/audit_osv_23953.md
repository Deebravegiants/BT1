# [M] ipv6: Fix signed integer overflow in l2tp_ip6_sendmsg

## Summary
Severity: Medium
Advisory: CVE-2022-49727
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49727
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.9.320, >=4.10.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: Fix signed integer overflow in l2tp_ip6_sendmsg

When len >= INT_MAX - transhdrlen, ulen = len + transhdrlen will be
overflow. To fix, we can follow what udpv6 does and subtract the
transhdrlen from the max.

## References
- https://git.kernel.org/stable/c/034246122f5c5e2e2a0b9fe04e24517920e9beb1
- https://git.kernel.org/stable/c/0e818d433fc2718fe4da044ffca7431812a7e04e
- https://git.kernel.org/stable/c/27a37755ceb401111ded76810359d3adc4b268a1
- https://git.kernel.org/stable/c/2cf73c7cb6125083408d77f43d0e84d86aed0000
- https://git.kernel.org/stable/c/2f42389d270f2304c8855b0b63498a5a4d0c053d
- https://git.kernel.org/stable/c/6c4e3486d21173d60925ef52e512cae727b43d30
- https://git.kernel.org/stable/c/b8879ca1fd7348b4d5db7db86dcb97f60c73d751
- https://git.kernel.org/stable/c/f638a84afef3dfe10554c51820c16e39a278c915
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49727.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49727
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
