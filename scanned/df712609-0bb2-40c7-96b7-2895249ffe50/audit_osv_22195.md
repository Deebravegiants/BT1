# [C] Buffer Overflow in xrdp

## Summary
Severity: Critical
Advisory: CVE-2022-23480
Aliases: GHSA-3jmx-f6hv-95wg
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-23480
Type: osv

## Details
xrdp is an open source project which provides a graphical login to remote machines using Microsoft Remote Desktop Protocol (RDP).
xrdp < v0.9.21 contain a buffer over flow in devredir_proc_client_devlist_announce_req() function. There are no known workarounds for this issue. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23480.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-3jmx-f6hv-95wg
- https://nvd.nist.gov/vuln/detail/CVE-2022-23480
- https://www.debian.org/security/2023/dsa-5502
