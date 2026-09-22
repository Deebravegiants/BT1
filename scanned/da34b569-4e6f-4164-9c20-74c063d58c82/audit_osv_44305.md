# [H] KVM: s390: vsie: zero stale crypto bits

## Summary
Severity: High
Advisory: CVE-2026-80921
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-80921
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.269, >=5.11.0 <5.15.220, >=5.16.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.18.49, >=6.19.0 <7.1.13, >=7.2.0 <7.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: vsie: zero stale crypto bits

When shadowing crypto access bits from a format0 apcb (crycb 0 or 1),
the bits 64..255 are unchanged from whatever is in the vsie page in the
crycb and thus in the apcb. This gives a nested guest potential access
to a device no longer available. Zero out the remaining bits.

## References
- https://git.kernel.org/stable/c/087c19cc60a8caa1a08e1e434c8be2caf6c27733
- https://git.kernel.org/stable/c/29b4f7bc2991313bd3e6f6fb8fdf1b173f086dd6
- https://git.kernel.org/stable/c/34d5b5b646c91cfb9338d7a12c955a70ffb8c66b
- https://git.kernel.org/stable/c/59d51550b5cb916bda037673a721a404b3b47a0d
- https://git.kernel.org/stable/c/7d23489f51109e3ebba5b5db8c5f0185af7b7fdf
- https://git.kernel.org/stable/c/935eeba276012916c76243e5cbb843efd8fdb75d
- https://git.kernel.org/stable/c/d110b3297f11ef227098b8a82ade2d5f123b7d2f
- https://git.kernel.org/stable/c/d4bcd2df6d0d2af916b4fe1a533958778ea7c45b
- https://git.kernel.org/stable/c/f6079dca67eccb5eabef9f72437948c66dc5131f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80921.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
