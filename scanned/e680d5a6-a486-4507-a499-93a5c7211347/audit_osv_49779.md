# [M] CVE-2019-19051

## Summary
Severity: Medium
Advisory: CVE-2019-19051
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19051
Type: osv

## Details
A memory leak in the i2400m_op_rfkill_sw_toggle() function in drivers/net/wimax/i2400m/op-rfkill.c in the Linux kernel before 5.3.11 allows attackers to cause a denial of service (memory consumption), aka CID-6f3ef5c25cc7.

## References
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4286-2/
- https://usn.ubuntu.com/4344-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4302-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4225-2/
- https://github.com/torvalds/linux/commit/6f3ef5c25cc762687a7341c18cbea5af54461407
