# [H] drm/sched: Fix bounds limiting when given a malformed entity

## Summary
Severity: High
Advisory: CVE-2023-52461
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2023-52461
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sched: Fix bounds limiting when given a malformed entity

If we're given a malformed entity in drm_sched_entity_init()--shouldn't
happen, but we verify--with out-of-bounds priority value, we set it to an
allowed value. Fix the expression which sets this limit.

## References
- https://git.kernel.org/stable/c/1470d173925d697b497656b93f7c5bddae2e64b2
- https://git.kernel.org/stable/c/2bbe6ab2be53858507f11f99f856846d04765ae3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52461.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
