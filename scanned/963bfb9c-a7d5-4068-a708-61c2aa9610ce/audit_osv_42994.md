# [C] KVM: s390: Fix unlikely race in try_get_locked_pte()

## Summary
Severity: Critical
Advisory: CVE-2026-72291
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72291
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: Fix unlikely race in try_get_locked_pte()

Fix an unlikely race in try_get_locked_pte(), which could have happened
if puds or pmds get unmapped between the p?dp_get() and p?d_offset()
functions.

## References
- https://git.kernel.org/stable/c/5670b7f927f8d98685f3f5873dbf9f8d7a5a63f3
- https://git.kernel.org/stable/c/ce587046baacdeb774b7756ab29b3f594e429004
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72291.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72291
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
