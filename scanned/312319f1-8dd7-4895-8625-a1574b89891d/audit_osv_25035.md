# [M] CVE-2023-2985

## Summary
Severity: Medium
Advisory: CVE-2023-2985
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-2985
Type: osv

## Details
A use after free flaw was found in hfsplus_put_super in fs/hfsplus/super.c in the Linux Kernel. This flaw could allow a local user to cause a denial of service problem.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=07db5e247ab5858439b14dd7cc1fe538b9efcf32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2985.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2985
