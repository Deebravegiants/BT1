# [H] rapidio/tsi721: prevent a bad dereference in tsi721_db_dpc()

## Summary
Severity: High
Advisory: CVE-2026-80645
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80645
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rapidio/tsi721: prevent a bad dereference in tsi721_db_dpc()

With a list_for_each() loop, if we don't find the item we are looking for
in the list, then the loop exits with the iterator, which is "dbell" in
this loop, pointing to invalid memory.

This code uses the "found" variable to determine if we have found the
doorbell we are looking for or not.  However, the problem that the "found"
variable needs to be set to false at the start of each iteration,
otherwise after the first correct doorbell, then everything is marked as
found.

Reset the "found" to false at the start of the iteration and move the
variable inside the loop.

## References
- https://git.kernel.org/stable/c/070f356ea4f419e4e85e4089381f4477f41d969e
- https://git.kernel.org/stable/c/13092966ba5d8fb214a4efeddc87f9ed0fd2f945
- https://git.kernel.org/stable/c/3b5c66e922aa6a3331915a14520848a5b3beccc7
- https://git.kernel.org/stable/c/81c06ef66c3ab6eeaa72eb790c90ae043cdb3d43
- https://git.kernel.org/stable/c/9e775c3199903d7c09a52530042b1198eab705bd
- https://git.kernel.org/stable/c/acd54f42abbbd806464468838dbc04efd203d2be
- https://git.kernel.org/stable/c/dc28a14f3e4546b2b06098d24177942540581a5f
- https://git.kernel.org/stable/c/fc15e3a30ddd950f009c76765331783b9af94a87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80645.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80645
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
