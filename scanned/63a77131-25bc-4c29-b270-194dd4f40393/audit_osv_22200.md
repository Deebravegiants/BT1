# [C] Out of Bound Read in xrdp

## Summary
Severity: Critical
Advisory: CVE-2022-23493
Aliases: GHSA-59wp-3wq6-jh5v
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-23493
Type: osv

## Details
xrdp is an open source project which provides a graphical login to remote machines using Microsoft Remote Desktop Protocol (RDP).
xrdp < v0.9.21 contain a Out of Bound Read in xrdp_mm_trans_process_drdynvc_channel_close() function. There are no known workarounds for this issue. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23493.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-59wp-3wq6-jh5v
- https://nvd.nist.gov/vuln/detail/CVE-2022-23493
- https://www.debian.org/security/2023/dsa-5502
