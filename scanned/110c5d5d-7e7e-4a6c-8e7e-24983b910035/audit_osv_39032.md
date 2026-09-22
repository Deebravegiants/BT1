# [H] libceph: Use u32 for non-negative values in ceph_monmap_decode()

## Summary
Severity: High
Advisory: CVE-2026-43405
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43405
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: Use u32 for non-negative values in ceph_monmap_decode()

This patch fixes unnecessary implicit conversions that change signedness
of blob_len and num_mon in ceph_monmap_decode().
Currently blob_len and num_mon are (signed) int variables. They are used
to hold values that are always non-negative and get assigned in
ceph_decode_32_safe(), which is meant to assign u32 values. Both
variables are subsequently used as unsigned values, and the value of
num_mon is further assigned to monmap->num_mon, which is of type u32.
Therefore, both variables should be of type u32. This is especially
relevant for num_mon. If the value read from the incoming message is
very large, it is interpreted as a negative value, and the check for
num_mon > CEPH_MAX_MON does not catch it. This leads to the attempt to
allocate a very large chunk of memory for monmap, which will most likely
fail. In this case, an unnecessary attempt to allocate memory is
performed, and -ENOMEM is returned instead of -EINVAL.

## References
- https://git.kernel.org/stable/c/08bc6173fd611ad5a40f472bf5f15b92aea0fe40
- https://git.kernel.org/stable/c/5f2806684b05bd24d05c091083b8e2517ba8ffac
- https://git.kernel.org/stable/c/770444611f047dbfd4517ec0bc1b179d40c2f346
- https://git.kernel.org/stable/c/86f7060cd638d6eb042e8ed780fb83a59ca0dcb3
- https://git.kernel.org/stable/c/b268984ae88cb0dcd7a8e8263962c748448e26e8
- https://git.kernel.org/stable/c/ba0a4df8c563536857dcbf7b4dbd0f2a15f57ace
- https://git.kernel.org/stable/c/ee5588e2bc41acb73f6676c0520420c107cd0140
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43405.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
