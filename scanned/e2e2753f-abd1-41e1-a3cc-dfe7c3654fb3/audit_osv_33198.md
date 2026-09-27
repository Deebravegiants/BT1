# [C] libceph: fix invalid accesses to ceph_connection_v1_info

## Summary
Severity: Critical
Advisory: CVE-2025-39880
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39880
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.194, >=5.16.0 <6.1.153, >=6.2.0 <6.6.107, >=6.7.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: fix invalid accesses to ceph_connection_v1_info

There is a place where generic code in messenger.c is reading and
another place where it is writing to con->v1 union member without
checking that the union member is active (i.e. msgr1 is in use).

On 64-bit systems, con->v1.auth_retry overlaps with con->v2.out_iter,
so such a read is almost guaranteed to return a bogus value instead of
0 when msgr2 is in use.  This ends up being fairly benign because the
side effect is just the invalidation of the authorizer and successive
fetching of new tickets.

con->v1.connect_seq overlaps with con->v2.conn_bufs and the fact that
it's being written to can cause more serious consequences, but luckily
it's not something that happens often.

## References
- https://git.kernel.org/stable/c/23538cfbeed87159a5ac6c61e7a6de3d8d4486a8
- https://git.kernel.org/stable/c/35dbbc3dbf8bccb2d77c68444f42c1e6d2d27983
- https://git.kernel.org/stable/c/591ea9c30737663a471b2bb07b27ddde86b020d5
- https://git.kernel.org/stable/c/6bd8b56899be0b514945f639a89ccafb8f8dfaef
- https://git.kernel.org/stable/c/cdbc9836c7afadad68f374791738f118263c5371
- https://git.kernel.org/stable/c/ea12ab684f8ae8a6da11a22c78d94a79e2163096
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39880.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
