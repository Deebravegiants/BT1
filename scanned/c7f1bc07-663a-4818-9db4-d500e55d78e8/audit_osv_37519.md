# [H] xen/privcmd: restrict usage in unprivileged domU

## Summary
Severity: High
Advisory: CVE-2026-31788
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-31788
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen/privcmd: restrict usage in unprivileged domU

The Xen privcmd driver allows to issue arbitrary hypercalls from
user space processes. This is normally no problem, as access is
usually limited to root and the hypervisor will deny any hypercalls
affecting other domains.

In case the guest is booted using secure boot, however, the privcmd
driver would be enabling a root user process to modify e.g. kernel
memory contents, thus breaking the secure boot feature.

The only known case where an unprivileged domU is really needing to
use the privcmd driver is the case when it is acting as the device
model for another guest. In this case all hypercalls issued via the
privcmd driver will target that other guest.

Fortunately the privcmd driver can already be locked down to allow
only hypercalls targeting a specific domain, but this mode can be
activated from user land only today.

The target domain can be obtained from Xenstore, so when not running
in dom0 restrict the privcmd driver to that target domain from the
beginning, resolving the potential problem of breaking secure boot.

This is XSA-482

---
V2:
- defer reading from Xenstore if Xenstore isn't ready yet (Jan Beulich)
- wait in open() if target domain isn't known yet
- issue message in case no target domain found (Jan Beulich)

## References
- http://www.openwall.com/lists/oss-security/2026/03/24/2
- http://www.openwall.com/lists/oss-security/2026/03/24/3
- http://www.openwall.com/lists/oss-security/2026/03/24/4
- http://www.openwall.com/lists/oss-security/2026/03/24/5
- http://www.openwall.com/lists/oss-security/2026/03/26/4
- https://git.kernel.org/stable/c/1879319d790f7d57622cdc22807b60ea78b56b6d
- https://git.kernel.org/stable/c/389bae9a4409934e8b8d4dbdaaf02a3ae71cf8e4
- https://git.kernel.org/stable/c/3ee5b9e3de4b8bdd74183d83205481c91a9effc8
- https://git.kernel.org/stable/c/453b8fb68f3641fea970db88b7d9a153ed2a37e8
- https://git.kernel.org/stable/c/4eb245ff0d33b618e097a2c23de5df56d4ad6969
- https://git.kernel.org/stable/c/78432d8f0372c71c518096395537fa12be7ff24e
- https://git.kernel.org/stable/c/87a803edb2ded911cb587c53bff179d2a2ed2a28
- https://git.kernel.org/stable/c/cbede2e833da1893afbea9b3ff29b5dda23a4a91
- http://xenbits.xen.org/xsa/advisory-482.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31788.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31788
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
