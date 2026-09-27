# [C] nvmet-fc: avoid scheduling association deletion twice

## Summary
Severity: Critical
Advisory: CVE-2025-40343
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40343
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-fc: avoid scheduling association deletion twice

When forcefully shutting down a port via the configfs interface,
nvmet_port_subsys_drop_link() first calls nvmet_port_del_ctrls() and
then nvmet_disable_port(). Both functions will eventually schedule all
remaining associations for deletion.

The current implementation checks whether an association is about to be
removed, but only after the work item has already been scheduled. As a
result, it is possible for the first scheduled work item to free all
resources, and then for the same work item to be scheduled again for
deletion.

Because the association list is an RCU list, it is not possible to take
a lock and remove the list entry directly, so it cannot be looked up
again. Instead, a flag (terminating) must be used to determine whether
the association is already in the process of being deleted.

## References
- https://git.kernel.org/stable/c/04d17540ef51e2c291eb863ca87fd332259b2d40
- https://git.kernel.org/stable/c/2f4852db87e25d4e226b25cb6f652fef9504360e
- https://git.kernel.org/stable/c/601ed47b2363c24d948d7bac0c23abc8bd459570
- https://git.kernel.org/stable/c/85e2ce1920cb511d57aae59f0df6ff85b28bf04d
- https://git.kernel.org/stable/c/c09ac9a63fc3aaf4670ad7b5e4f5afd764424154
- https://git.kernel.org/stable/c/f2537be4f8421f6495edfa0bc284d722f253841d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40343.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40343
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
