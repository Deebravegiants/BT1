# [H] apparmor: check label build before no_new_privs test

## Summary
Severity: High
Advisory: CVE-2026-72460
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72460
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: check label build before no_new_privs test

aa_change_profile() builds a replacement label with
fn_label_build_in_scope() before the no_new_privs subset check. The build
helper can fail and return NULL or an ERR_PTR, but the result was passed
to aa_label_is_unconfined_subset() before the existing IS_ERR_OR_NULL()
check.

Reuse the existing target-label build failure handling immediately after
the build. This preserves the current audit handling while preventing the
subset helper from dereferencing an invalid label.

## References
- https://git.kernel.org/stable/c/31cb109db5e6322ed22304fd5c0dedbaa438d6d3
- https://git.kernel.org/stable/c/a29f06db44b4c94597ded58f639eed3e21781ac3
- https://git.kernel.org/stable/c/a58cafd38b46fb1a2220e2fbbcfe291ea75fa147
- https://git.kernel.org/stable/c/b7c45c05a396a017c49ac7949de240a0dfc0ac4e
- https://git.kernel.org/stable/c/cfc224866530a6842b6c2d2d30ef6a9b0e64bb9c
- https://git.kernel.org/stable/c/d82160132345688a09cbaa648cfdd16bb32e8ea2
- https://git.kernel.org/stable/c/d84bb195d208adbf77f012ca2a96e11163f6def1
- https://git.kernel.org/stable/c/ec926b2a351eeeb31e6c9aee02e0c32f94b5588f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72460.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72460
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
