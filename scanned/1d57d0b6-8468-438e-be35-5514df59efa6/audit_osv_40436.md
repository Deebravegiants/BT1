# [H] KVM: arm64: nv: Fix handling of XN[0] when !FEAT_XNX

## Summary
Severity: High
Advisory: CVE-2026-53200
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53200
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Fix handling of XN[0] when !FEAT_XNX

XN has already been extracted from its bitfield position so using
FIELD_PREP() on the mask that clears XN[0] is completely broken, having
the effect of unconditionally granting execute permissions...

Fix the obvious mistake by manipulating the right bit.

## References
- https://git.kernel.org/stable/c/49b32ddb87a3a109afecea89e55d70f73956b8bc
- https://git.kernel.org/stable/c/b95976c2ea446044553a5f469c0bae13553d75ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53200.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53200
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
