# [C] xrdp: Heap buffer overflow in EGFX channel

## Summary
Severity: Critical
Advisory: CVE-2026-35512
Aliases: GHSA-jg6p-7fg8-9hh6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-35512
Type: osv

## Details
xrdp is an open source RDP server. Versions through 0.10.5 have a heap-based buffer overflow in the EGFX (graphics dynamic virtual channel) implementation due to insufficient validation of client-controlled size parameters, allowing an out-of-bounds write via crafted PDUs. Pre-authentication exploitation can crash the process, while post-authentication exploitation may achieve remote code execution. This issue has been fixed in version 0.10.6. If users are unable to immediately update, they should run xrdp as a non-privileged user (default since 0.10.2) to limit the impact of successful exploitation.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35512.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-jg6p-7fg8-9hh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35512
