# [H] drm/vc4: Prevent shader BO mappings from becoming writable

## Summary
Severity: High
Advisory: CVE-2026-68445
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68445
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vc4: Prevent shader BO mappings from becoming writable

vc4_gem_object_mmap() rejects a writable mapping of a validated shader
BO, but leaves VM_MAYWRITE set.  Userspace can map the BO read-only and
then turn it writable with mprotect().

Validated shader BOs must stay read-only: the validator checks the
instructions once and the GPU trusts them afterwards.  A writable
mapping lets userspace rewrite the code after validation, bypassing the
validator.

Clear VM_MAYWRITE on the read-only path so the mapping cannot be
upgraded, as i915 already does for its read-only objects.

## References
- https://git.kernel.org/stable/c/019e6ad247f7fd038d2e009789f6d9bfcccb1ae7
- https://git.kernel.org/stable/c/0c9e6367639548307d3f578f6943ce72c9d39087
- https://git.kernel.org/stable/c/6deaa317201851c644c431b57682e54d06b35838
- https://git.kernel.org/stable/c/9f0ee411fc2d76333d6087c5862ffa907cf7a175
- https://git.kernel.org/stable/c/fe168ef1d232d734d9998fd74822e2e20930dfff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68445
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
