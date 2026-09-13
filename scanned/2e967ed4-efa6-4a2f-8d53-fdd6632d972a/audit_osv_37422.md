# [H] KVM: arm64: Fix the descriptor address in __kvm_at_swap_desc()

## Summary
Severity: High
Advisory: CVE-2026-31553
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31553
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Fix the descriptor address in __kvm_at_swap_desc()

Using "(u64 __user *)hva + offset" to get the virtual addresses of S1/S2
descriptors looks really wrong, if offset is not zero. What we want to get
for swapping is hva + offset, not hva + offset*8. ;-)

Fix it.

## References
- https://git.kernel.org/stable/c/0496acc42fb51eee040b5170cec05cec41385540
- https://git.kernel.org/stable/c/4307e05e568782fc92eff651b09ee5dee88a058d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31553.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31553
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
