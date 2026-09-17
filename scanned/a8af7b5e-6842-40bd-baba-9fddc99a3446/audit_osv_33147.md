# [H] lib/crypto: arm/poly1305: Fix register corruption in no-SIMD contexts

## Summary
Severity: High
Advisory: CVE-2025-39802
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-39802
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib/crypto: arm/poly1305: Fix register corruption in no-SIMD contexts

Restore the SIMD usability check that was removed by commit 773426f4771b
("crypto: arm/poly1305 - Add block-only interface").

This safety check is cheap and is well worth eliminating a footgun.
While the Poly1305 functions should not be called when SIMD registers
are unusable, if they are anyway, they should just do the right thing
instead of corrupting random tasks' registers and/or computing incorrect
MACs.  Fixing this is also needed for poly1305_kunit to pass.

Just use may_use_simd() instead of the original crypto_simd_usable(),
since poly1305_kunit won't rely on crypto_simd_disabled_for_test.

## References
- https://git.kernel.org/stable/c/52c3e242f4d0043186b70d65460ba1767f27494a
- https://git.kernel.org/stable/c/87bdfba903be7084cb3ee04032b14a81181fe413
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39802.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39802
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
