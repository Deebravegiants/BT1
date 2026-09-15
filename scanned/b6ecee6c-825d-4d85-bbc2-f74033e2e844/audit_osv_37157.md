# [C] Improper authorization in device bulk actions and device update API allows cross-organization device control

## Summary
Severity: Critical
Advisory: CVE-2026-28806
Aliases: EEF-CVE-2026-28806, GHSA-f8fr-mccc-xvcx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-28806
Type: osv

## Details
Improper Authorization vulnerability in nerves-hub nerves_hub_web allows cross-organization device control via device bulk actions and device update API.

Missing authorization checks in the device bulk actions and device update API endpoints allow authenticated users to target devices belonging to other organizations and perform actions outside of their privilege level.

An attacker can select devices outside of their organization by manipulating device identifiers and perform management actions on them, such as moving them to products they control. This may allow attackers to interfere with firmware updates, access device functionality exposed by the platform, or disrupt device connectivity.

In environments where additional features such as remote console access are enabled, this could lead to full compromise of affected devices.

This issue affects nerves_hub_web: from 1.0.0 before 2.4.0.

## References
- https://cna.erlef.org/cves/CVE-2026-28806.html
- https://ghcr.io
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-28806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28806.json
- https://github.com/nerves-hub/nerves_hub_web/security/advisories/GHSA-f8fr-mccc-xvcx
- https://nvd.nist.gov/vuln/detail/CVE-2026-28806
- https://github.com/nerves-hub/nerves_hub_web/commit/1f69c9d595684a4650c3ac702f3dc7c5bcd7526c
- https://github.com/nerves-hub/nerves_hub_web
- https://github.com/nerves-hub/nerves_hub_web.git
