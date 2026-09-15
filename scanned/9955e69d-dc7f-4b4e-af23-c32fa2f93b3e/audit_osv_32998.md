# [H] drm/xe/pf: Clear all LMTT pages on alloc

## Summary
Severity: High
Advisory: CVE-2025-38511
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38511
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/pf: Clear all LMTT pages on alloc

Our LMEM buffer objects are not cleared by default on alloc
and during VF provisioning we only setup LMTT PTEs for the
actually provisioned LMEM range. But beyond that valid range
we might leave some stale data that could either point to some
other VFs allocations or even to the PF pages.

Explicitly clear all new LMTT page to avoid the risk that a
malicious VF would try to exploit that gap.

While around add asserts to catch any undesired PTE overwrites
and low-level debug traces to track LMTT PT life-cycle.

(cherry picked from commit 3fae6918a3e27cce20ded2551f863fb05d4bef8d)

## References
- https://git.kernel.org/stable/c/5d21892c2e15b6a27f8bc907693eca7c6b7cc269
- https://git.kernel.org/stable/c/705a412a367f383430fa34bada387af2e52eb043
- https://git.kernel.org/stable/c/ff4b8c9ade1b82979fdd01e6f45b60f92eed26d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38511.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38511
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
