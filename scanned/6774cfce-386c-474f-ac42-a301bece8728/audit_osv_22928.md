# [M] CVE-2022-4127

## Summary
Severity: Medium
Advisory: CVE-2022-4127
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-28
Source: https://osv.dev/vulnerability/CVE-2022-4127
Type: osv

## Details
A NULL pointer dereference issue was discovered in the Linux kernel in io_files_update_with_index_alloc. A local user could use this flaw to potentially crash the system causing a denial of service.

## References
- https://lore.kernel.org/all/d5a19c1e-9968-e22e-5917-c3139c5e7e89%40kernel.dk/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4127.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4127
- https://github.com/torvalds/linux/commit/d785a773bed966a75ca1f11d108ae1897189975b
