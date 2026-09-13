# [H] drm/amd/display: increase max link count and fix link->enc NULL pointer access

## Summary
Severity: High
Advisory: CVE-2025-40354
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-40354
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: increase max link count and fix link->enc NULL pointer access

[why]
1.) dc->links[MAX_LINKS] array size smaller than actual requested.
max_connector + max_dpia + 4 virtual = 14.
increase from 12 to 14.

2.) hw_init() access null LINK_ENC for dpia non display_endpoint.

(cherry picked from commit d7f5a61e1b04ed87b008c8d327649d184dc5bb45)

## References
- https://git.kernel.org/stable/c/a3fc0d36cfb927f8986b83bf5fba47dbedad3c63
- https://git.kernel.org/stable/c/bec947cbe9a65783adb475a5fb47980d7b4f4796
- https://git.kernel.org/stable/c/f28092be4e12b7df9e4f415d25bf0d767bc2d9ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40354.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40354
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
