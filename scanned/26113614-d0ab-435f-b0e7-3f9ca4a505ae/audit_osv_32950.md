# [H] genirq/irq_sim: Initialize work context pointers properly

## Summary
Severity: High
Advisory: CVE-2025-38408
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38408
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.120, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

genirq/irq_sim: Initialize work context pointers properly

Initialize `ops` member's pointers properly by using kzalloc() instead of
kmalloc() when allocating the simulation work context. Otherwise the
pointers contain random content leading to invalid dereferencing.

## References
- https://git.kernel.org/stable/c/186df821de0f34490ed5fc0861243748b2483861
- https://git.kernel.org/stable/c/19bd7597858dd15802c1d99fcc38e528f469080a
- https://git.kernel.org/stable/c/7f73d1def72532bac4d55ea8838f457a6bed955c
- https://git.kernel.org/stable/c/8a2277a3c9e4cc5398f80821afe7ecbe9bdf2819
- https://git.kernel.org/stable/c/c71aa4bb528ae6f8fd7577a0a39e5a03c60b04fb
- https://git.kernel.org/stable/c/ec3656a8cb428d763def32bc2fa695f94be23629
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38408.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
