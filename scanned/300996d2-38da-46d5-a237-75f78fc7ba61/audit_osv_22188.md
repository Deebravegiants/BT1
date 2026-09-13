# [M] Buffer Overflow in xrdp

## Summary
Severity: Medium
Advisory: CVE-2022-23468
Aliases: GHSA-8c2f-mw8m-qpx6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-23468
Type: osv

## Details
xrdp is an open source project which provides a graphical login to remote machines using Microsoft Remote Desktop Protocol (RDP).
xrdp < v0.9.21 contain a buffer over flow in xrdp_login_wnd_create() function. There are no known workarounds for this issue. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23468.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-8c2f-mw8m-qpx6
- https://nvd.nist.gov/vuln/detail/CVE-2022-23468
- https://www.debian.org/security/2023/dsa-5502
