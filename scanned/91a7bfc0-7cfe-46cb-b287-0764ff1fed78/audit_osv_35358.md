# [H] KVM: s390: Fix gmap_helper_zap_one_page() again

## Summary
Severity: High
Advisory: CVE-2025-71155
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71155
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: Fix gmap_helper_zap_one_page() again

A few checks were missing in gmap_helper_zap_one_page(), which can lead
to memory corruption in the guest under specific circumstances.

Add the missing checks.

## References
- https://git.kernel.org/stable/c/2af2abbcbf8573100288e8f8aea2dab8a2a0ceb7
- https://git.kernel.org/stable/c/2f393c228cc519ddf19b8c6c05bf15723241aa96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71155.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
