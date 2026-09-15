# [M] XianYuLauncher: Legacy Microsoft account OAuth sign-in flow lacks PKCE and state validation

## Summary
Severity: Medium
Advisory: CVE-2026-48991
Aliases: GHSA-q6r9-qxmf-8hfx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-48991
Type: osv

## Details
XianYuLauncher is a Minecraft Java Edition launcher. In versions prior to 1.5.5, sensitive authentication artifacts could be exposed during a user-initiated login under certain local attack conditions. Affected versions relied on a fixed localhost redirect URI without PKCE or state validation. Exploitation is most likely to occur when an attacker is able to observe, intercept, or otherwise interfere with the local authentication flow on the same device. This issue has been fixed in version 1.5.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48991.json
- https://github.com/XianYuLauncher/XianYuLauncher/security/advisories/GHSA-q6r9-qxmf-8hfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-48991
- https://github.com/XianYuLauncher/XianYuLauncher/pull/213
