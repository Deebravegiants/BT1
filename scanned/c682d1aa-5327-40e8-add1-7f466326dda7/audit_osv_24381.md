# [M] CVE-2023-1195

## Summary
Severity: Medium
Advisory: CVE-2023-1195
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-1195
Type: osv

## Details
A use-after-free flaw was found in reconn_set_ipaddr_from_hostname in fs/cifs/connect.c in the Linux kernel. The issue occurs when it forgets to set the free pointer server->hostname to NULL, leading to an invalid pointer request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1195.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1195
- https://github.com/torvalds/linux/commit/153695d36ead0ccc4d0256953c751cabf673e621
