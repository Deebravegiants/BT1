# [M] Drivers: vmbus: Check for channel allocation before looking up relids

## Summary
Severity: Medium
Advisory: CVE-2023-53273
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53273
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.178, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Drivers: vmbus: Check for channel allocation before looking up relids

relid2channel() assumes vmbus channel array to be allocated when called.
However, in cases such as kdump/kexec, not all relids will be reset by the host.
When the second kernel boots and if the guest receives a vmbus interrupt during
vmbus driver initialization before vmbus_connect() is called, before it finishes,
or if it fails, the vmbus interrupt service routine is called which in turn calls
relid2channel() and can cause a null pointer dereference.

Print a warning and error out in relid2channel() for a channel id that's invalid
in the second kernel.

## References
- https://git.kernel.org/stable/c/176c6b4889195fbe7016d9401175b48c5c9edf68
- https://git.kernel.org/stable/c/1eb65c8687316c65140b48fad27133d583178e15
- https://git.kernel.org/stable/c/8c3f0ae5435fd20bb1e3a8308488aa6ac33151ee
- https://git.kernel.org/stable/c/a5c44f3446a0565139b7d8abc78f58b86c398123
- https://git.kernel.org/stable/c/c373e49fbb87aa177819866ed9194ebc5414dfd6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53273.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
