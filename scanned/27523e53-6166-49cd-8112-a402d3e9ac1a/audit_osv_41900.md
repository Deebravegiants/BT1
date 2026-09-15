# [C] netfs: Fix netfs_read_to_pagecache() to pause on subreq failure

## Summary
Severity: Critical
Advisory: CVE-2026-64066
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64066
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix netfs_read_to_pagecache() to pause on subreq failure

Fix netfs_read_to_pagecache() so that it pauses the generation of new
subrequests if an already-issued subrequest fails.

## References
- https://git.kernel.org/stable/c/0256e79ce42101ad036edd4205bccca621ea0927
- https://git.kernel.org/stable/c/884c4c4f35e577aba6a0593c80cbea9ca5e6e2b8
- https://git.kernel.org/stable/c/8a8c0cfdf4658fc5b295b7fc87be56e0d76741f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64066.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
