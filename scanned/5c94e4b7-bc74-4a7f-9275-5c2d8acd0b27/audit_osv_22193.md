# [C] Out of Bound Write in xrdp

## Summary
Severity: Critical
Advisory: CVE-2022-23478
Aliases: GHSA-2f49-wwpm-78pj
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-23478
Type: osv

## Details
xrdp is an open source project which provides a graphical login to remote machines using Microsoft Remote Desktop Protocol (RDP).
xrdp < v0.9.21 contain a Out of Bound Write in xrdp_mm_trans_process_drdynvc_channel_open() function. There are no known workarounds for this issue. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23478.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-2f49-wwpm-78pj
- https://nvd.nist.gov/vuln/detail/CVE-2022-23478
- https://www.debian.org/security/2023/dsa-5502
