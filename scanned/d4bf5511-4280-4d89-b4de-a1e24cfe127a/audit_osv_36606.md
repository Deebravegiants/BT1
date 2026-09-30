# [M] FreeRDP has a heap-use-after-free in urb_bulk_transfer_cb

## Summary
Severity: Medium
Advisory: CVE-2026-24681
Aliases: GHSA-ccvv-hg2w-6x9j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24681
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, aAsynchronous bulk transfer completions can use a freed channel callback after URBDRC channel close, leading to a use after free in urb_write_completion. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24681.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-ccvv-hg2w-6x9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-24681
- https://github.com/FreeRDP/FreeRDP/commit/414f701464929c217f2509bcbd6d2c1f00f7ed73
