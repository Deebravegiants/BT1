# [M] CVE-2022-4128

## Summary
Severity: Medium
Advisory: CVE-2022-4128
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-28
Source: https://osv.dev/vulnerability/CVE-2022-4128
Type: osv

## Details
A NULL pointer dereference issue was discovered in the Linux kernel in the MPTCP protocol when traversing the subflow list at disconnect time. A local user could use this flaw to potentially crash the system causing a denial of service.

## References
- https://lore.kernel.org/netdev/20220708233610.410786-2-mathew.j.martineau%40linux.intel.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4128.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4128
- https://github.com/torvalds/linux/commit/5c835bb142d4
