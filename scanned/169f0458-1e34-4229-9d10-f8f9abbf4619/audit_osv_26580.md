# [M] accel/habanalabs: fix mem leak in capture user mappings

## Summary
Severity: Medium
Advisory: CVE-2023-53367
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53367
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/habanalabs: fix mem leak in capture user mappings

This commit fixes a memory leak caused when clearing the user_mappings
info when a new context is opened immediately after user_mapping is
captured and a hard reset is performed.

## References
- https://git.kernel.org/stable/c/314a7ffd7c196b27eedd50cb7553029e17789b55
- https://git.kernel.org/stable/c/973e0890e5264cb075ef668661cad06b67777121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53367.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
