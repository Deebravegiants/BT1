# [M] CVE-2023-3359

## Summary
Severity: Medium
Advisory: CVE-2023-3359
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-3359
Type: osv

## Details
An issue was discovered in the Linux kernel brcm_nvram_parse in drivers/nvmem/brcm_nvram.c. Lacks for the check of the return value of kzalloc() can cause the NULL Pointer Dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b0576ade3aaf24b376ea1a4406ae138e2a22b0c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3359.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3359
