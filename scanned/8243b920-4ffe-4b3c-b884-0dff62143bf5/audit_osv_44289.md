# [H] thunderbolt: Fix bandwidth group reservation indexing

## Summary
Severity: High
Advisory: CVE-2026-80736
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80736
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Fix bandwidth group reservation indexing

Valid bandwidth group IDs range from 1 through MAX_GROUPS, while Group
ID 0 is reserved. tb_consumed_dp_bandwidth() uses the Group ID directly
to index its local group_reserved[] array.

The array currently has MAX_GROUPS entries, so its valid indices are 0
through MAX_GROUPS - 1. Group ID MAX_GROUPS therefore accesses one
element past the end, and the final group's reserved bandwidth is not
included when the array is summed.

Give group_reserved[] MAX_GROUPS + 1 entries so direct Group ID
indexing covers the reserved ID 0 and valid IDs 1 through MAX_GROUPS.

## References
- https://git.kernel.org/stable/c/0a8c9ed4f166216642a8c084f0de415169c88088
- https://git.kernel.org/stable/c/0bfb67ba366cd68d1d0ad935760577bae1d5df27
- https://git.kernel.org/stable/c/9977321835c7ae71d12a43bed7baa5bd514d01c3
- https://git.kernel.org/stable/c/d2ee4d47aacbd2ba456092eeec670dba35fde291
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80736.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80736
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
