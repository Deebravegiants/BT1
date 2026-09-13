# [H] libceph: Fix potential null-ptr-deref in decode_choose_args()

## Summary
Severity: High
Advisory: CVE-2026-52957
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52957
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Fix potential null-ptr-deref in decode_choose_args()

A message of type CEPH_MSG_OSD_MAP contains an OSD map that itself
contains a CRUSH map. When decoding this CRUSH map in crush_decode(), an
array of max_buckets CRUSH buckets is decoded, where some indices may
not refer to actual buckets and are therefore set to NULL. The received
CRUSH map may optionally contain choose_args that get decoded in
decode_choose_args(). When decoding a crush_choose_arg_map, a series of
choose_args for different buckets is decoded, with the bucket_index
being read from the incoming message. It is only checked that the bucket
index does not exceed max_buckets, but not that it doesn't point to an
index with a NULL bucket. If a (potentially corrupted) message contains
a crush_choose_arg_map including such a bucket_index, a null pointer
dereference may occur in the subsequent processing when attempting to
access the bucket with the given index.

This patch fixes the issue by extending the affected check. Now, it is
only attempted to access the bucket if it is not NULL.

## References
- https://git.kernel.org/stable/c/28b0a2ab8c82d0bbdeb8013029c67c978ce6e4bf
- https://git.kernel.org/stable/c/301286c0ccd37d66b0e40786fd35a4f19cdbd88a
- https://git.kernel.org/stable/c/312ec973efac0efb9b9ed64214235910e9ecbaa8
- https://git.kernel.org/stable/c/7169f326a23d0f547fcd90e68b72fd387622e126
- https://git.kernel.org/stable/c/a20e16ebfe2fa65348eb4b2dc7deac330ce03e9c
- https://git.kernel.org/stable/c/d55ffad8d422b5d1cc44dad32bd3d25f4471cd9f
- https://git.kernel.org/stable/c/d7a65a34d2453f8cd3e0cc0e1319740af7e24276
- https://git.kernel.org/stable/c/f2f95e6d4b97e70bb876139b0583fc8079983f85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52957.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52957
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
