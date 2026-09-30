# [C] libceph: Fix multiplication overflow in decode_new_up_state_weight()

## Summary
Severity: Critical
Advisory: CVE-2026-68158
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68158
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Fix multiplication overflow in decode_new_up_state_weight()

If a message of type CEPH_MSG_OSD_MAP contains a (maliciously) corrupted
osdmap, out-of-bounds memory accesses may occur in
decode_new_up_state_weight(). This happens because the bounds check for
the new_state part is based on calculating its length depending on a len
value read from the incoming message. This calculation may overflow
leading to an incorrect bounds check. Subsequently, out-of-bounds reads
may occur when decoding this part.

This patch switches the multiplication to use check_mul_overflow() to
abort processing the osdmap if an overflow occurred. Therefore,
osdmaps/messages containing large values for len that result in a
multiplication overflow are treated as invalid.

[ idryomov: rename new_state_len -> new_state_item_size, formatting ]

## References
- https://git.kernel.org/stable/c/05c90e059269f087becfcce23348496085835c29
- https://git.kernel.org/stable/c/143ba49ead77ec483c0326f8aaad8649874e99c4
- https://git.kernel.org/stable/c/1732d89dfcd74f6fde9ce70900d316c4a151c153
- https://git.kernel.org/stable/c/2ceee3b77b83052648c40fef965f836fd7699d26
- https://git.kernel.org/stable/c/98917a499ec7064c14fc56d180a4fd636fc2784c
- https://git.kernel.org/stable/c/bee4b5b53e7bff0467fd916cc44c9b190733c6bd
- https://git.kernel.org/stable/c/e4473751cc37db41f3f7da25d64a23e0c74570f1
- https://git.kernel.org/stable/c/f6961070c326bd158c38fa48756cde2bd78c4aaa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68158.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68158
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
