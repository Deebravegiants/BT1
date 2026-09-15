# [C] KVM: s390: pci: Fix NULL dereference on AIBV allocation failure

## Summary
Severity: Critical
Advisory: CVE-2026-80684
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80684
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: pci: Fix NULL dereference on AIBV allocation failure

The airq_iv_create() can return NULL on failure, but the return value was
never checked. If it fails, zdev->aibv will be NULL and fail when
dereferenced in kvm_zpci_set_airq(). Add a NULL check and free the
previously allocated AISB bit and zdev->aisb on failure.

## References
- https://git.kernel.org/stable/c/0a95abe964400771ad82b027d7b84a0d183cd0db
- https://git.kernel.org/stable/c/8bf09b9b7d3232806df95f409581f8a9fd99a3fa
- https://git.kernel.org/stable/c/96099486b63985801c9c6ef22505e9aa635b2d20
- https://git.kernel.org/stable/c/d1a103dc9016c25e7423ce5841a5cc2df76d59f3
- https://git.kernel.org/stable/c/df947d85e164a50a29d43a96e814f69ab1d0f7ed
- https://git.kernel.org/stable/c/e137d082325bbcae780087b57501d38585e625d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80684.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80684
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
