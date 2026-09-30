# [H] Integer Overflow in xrdp

## Summary
Severity: High
Advisory: CVE-2022-23484
Aliases: GHSA-rqfx-5fv8-q9c6
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-23484
Type: osv

## Details
xrdp is an open source project which provides a graphical login to remote machines using Microsoft Remote Desktop Protocol (RDP).
xrdp < v0.9.21 contain a Integer Overflow in xrdp_mm_process_rail_update_window_text() function. There are no known workarounds for this issue. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23484.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-rqfx-5fv8-q9c6
- https://nvd.nist.gov/vuln/detail/CVE-2022-23484
- https://www.debian.org/security/2023/dsa-5502
