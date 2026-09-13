# [H] KVM: s390: pci: Fix handling of AIF enable without AISB

## Summary
Severity: High
Advisory: CVE-2026-68454
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-68454
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: pci: Fix handling of AIF enable without AISB

When a guest seeks to register IRQs without a summary bit specified,
ensure that the associated GAITE then stores 0 for the guest AISB
location instead of virt_to_phys(page_address(NULL)).

## References
- https://git.kernel.org/stable/c/124a3769c43713a11a93a821b313e61ad5110cb8
- https://git.kernel.org/stable/c/3e3aa6da87d30a0064a17b836685cd43c90a3572
- https://git.kernel.org/stable/c/3ef3190e30601b2688bdc64169b938b8d7f42010
- https://git.kernel.org/stable/c/d48b9b096d11e31690c0a4988f65f21b64c01b2a
- https://git.kernel.org/stable/c/df72596278b0e22dac5ef2881e9221a3a2c4ed11
- https://git.kernel.org/stable/c/f887df91826e72b570c5e9298e66dd929f09edde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
