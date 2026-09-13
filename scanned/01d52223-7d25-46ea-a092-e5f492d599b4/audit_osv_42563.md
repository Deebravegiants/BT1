# [H] libceph: bound get_version reply decode to front len

## Summary
Severity: High
Advisory: CVE-2026-68433
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68433
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: bound get_version reply decode to front len

handle_get_version_reply() uses msg->front_alloc_len as the decode
boundary for MON_GET_VERSION_REPLY.  That is the size of the reused
reply buffer, not the number of bytes actually received.

A truncated reply can therefore pass ceph_decode_need() and decode the
second u64 from stale tail bytes left in the buffer by an earlier
message, causing an uninitialized memory read.

Use msg->front.iov_len as the receive-side decode boundary, matching
other libceph reply handlers and limiting decoding to the bytes that
were actually read from the wire.

## References
- https://git.kernel.org/stable/c/0d934c934ec746d53fc7e4f53239792647bbae63
- https://git.kernel.org/stable/c/1307028f082756bf453e1889aee9983d30643a4b
- https://git.kernel.org/stable/c/340e0386aa39da181015bee38f309018c335ce16
- https://git.kernel.org/stable/c/4e7ebfaa0d14cf50e44041bfde38070d6dbc019f
- https://git.kernel.org/stable/c/72a35070fcefa229b1b031aa7482ad3788e18f07
- https://git.kernel.org/stable/c/d3c32939fa0e3ee9b883b9a0fd1972c5c444e3d0
- https://git.kernel.org/stable/c/d60de8253c85a02d0e6194b0735e7a562981a04c
- https://git.kernel.org/stable/c/f6cbf6878f3a1503c872ba8f1e69a58ee68d8b2e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68433
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
