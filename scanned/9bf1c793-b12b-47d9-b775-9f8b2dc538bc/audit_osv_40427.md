# [H] RDMA/core: Validate the passed in fops for ib_get_ucaps()

## Summary
Severity: High
Advisory: CVE-2026-53188
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53188
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Validate the passed in fops for ib_get_ucaps()

Sashiko pointed out it is not safe to rely only on the devt because
char/block alias so if the user finds a block device with the same dev_t
it can masquerade as a ucap cdev fd.

Test the f_ops to only accept authentic cdevs.

## References
- https://git.kernel.org/stable/c/4a1b1ac2744694a2ecd66a84bdb1445f4ef24bee
- https://git.kernel.org/stable/c/96b6e98ff12d50ed5817230c6f1188e1150d225d
- https://git.kernel.org/stable/c/aa181287ebdcc53ee0ba5c2f8243e2d541ebc19b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53188.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53188
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
