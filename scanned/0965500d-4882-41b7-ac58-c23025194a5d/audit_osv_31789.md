# [H] drm/amdgpu: avoid buffer overflow attach in smu_sys_set_pp_table()

## Summary
Severity: High
Advisory: CVE-2025-21780
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21780
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: avoid buffer overflow attach in smu_sys_set_pp_table()

It malicious user provides a small pptable through sysfs and then
a bigger pptable, it may cause buffer overflow attack in function
smu_sys_set_pp_table().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1abb2648698bf10783d2236a6b4a7ca5e8021699
- https://git.kernel.org/stable/c/231075c5a8ea54f34b7c4794687baa980814e6de
- https://git.kernel.org/stable/c/2498d2db1d35e88a2060ea191ae75dce853dd084
- https://git.kernel.org/stable/c/3484ea33157bc7334f57e64826ec5a4bf992151a
- https://git.kernel.org/stable/c/e43a8b9c4d700ffec819c5043a48769b3e7d9cab
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21780.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21780
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
