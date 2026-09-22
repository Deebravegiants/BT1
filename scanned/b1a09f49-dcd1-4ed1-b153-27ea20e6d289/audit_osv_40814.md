# [H] xrdp: No authentication required with Xvnc backend on RHEL 9

## Summary
Severity: High
Advisory: CVE-2026-55626
Aliases: GHSA-m3xx-cpc4-982r
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-55626
Type: osv

## Details
xrdp is an open source RDP server. In versions 0.10.6 and prior, when an authenticated user session is initialized using the Xvnc backend over UNIX domain sockets, the Xvnc process is launched with insufficient authentication mechanisms. A local authenticated attacker could exploit this vulnerability to bypass intended session isolation, allowing them to unauthorizedly view or control the active desktop sessions of other users on the same system. Users using other backends, such as xorgxrdp or Xvnc over TCP sockets, are not affected. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55626.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-m3xx-cpc4-982r
- https://nvd.nist.gov/vuln/detail/CVE-2026-55626
