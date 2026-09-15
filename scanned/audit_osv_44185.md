# [C] libceph: fix OOB read in decode_watchers() via missing bounds check

## Summary
Severity: Critical
Advisory: CVE-2026-80557
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80557
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.47, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: fix OOB read in decode_watchers() via missing bounds check

ceph_start_decoding() validates that struct_len bytes remain in the
buffer after the encoding header, but accepts struct_len=0 as valid:
ceph_decode_need(p, end, 0, bad) always passes. When a malicious or
compromised OSD sends an obj_list_watch_response_t reply with
struct_len=0, ceph_start_decoding() returns success with p == end,
leaving zero bytes guaranteed for subsequent reads.

The immediately following ceph_decode_32(p) in decode_watchers() has
no preceding bounds check. With p == end this is a 4-byte read past
the validated buffer boundary. The garbage value is then passed
directly to kzalloc_objs() as the watcher count.

The sibling function decode_watcher() already uses the safe variants
(ceph_decode_copy_safe, ceph_decode_64_safe, ceph_decode_skip_32)
after its own ceph_start_decoding() call. decode_watchers() is the
only site that uses the bare variant, confirming an oversight.

Fix by replacing ceph_decode_32(p) with ceph_decode_32_safe(p, end,
*num_watchers, bad), consistent with the established pattern.

Attacker model: a malicious or compromised OSD in a multi-tenant Ceph
deployment (e.g. cloud) can trigger this against any kernel client
that calls CEPH_OSD_OP_LIST_WATCHERS, without any further privileges
beyond OSD session establishment.

[ idryomov: trim changelog ]

## References
- https://git.kernel.org/stable/c/00ead17c7de137a692edee59f2772e6af687e8eb
- https://git.kernel.org/stable/c/1c824e7c75bb4adf19553dd4ea944a5d83096be8
- https://git.kernel.org/stable/c/7130d94846dadbb97b6b7f4d78a3a7bba6e3daa1
- https://git.kernel.org/stable/c/85479b7d65b4ebcb07fbbe57230976793974ab4a
- https://git.kernel.org/stable/c/c59219a6b62d74936963983e5815524c3de8dd79
- https://git.kernel.org/stable/c/cb8246e5846dbbe34930903a90c7a90dd8e5910b
- https://git.kernel.org/stable/c/eab3eeb68bfc639d74f27256f05546af5c4f787d
- https://git.kernel.org/stable/c/f161be39201eb5f9b1f58fb8f90b8a9cd3931eb6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80557.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80557
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
