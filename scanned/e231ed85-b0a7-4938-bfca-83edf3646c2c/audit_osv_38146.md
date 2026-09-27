# [M] Avahi: Reachable assertion in `transport_flags_from_domain()` via conflicting publish flags crashes avahi-daemon

## Summary
Severity: Medium
Advisory: CVE-2026-34933
Aliases: GHSA-w65r-6gxh-vhvc
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34933
Type: osv

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. Prior to version 0.9-rc4, any unprivileged local user can crash avahi-daemon by sending a single D-Bus method call with conflicting publish flags. This issue has been patched in version 0.9-rc4.

## References
- http://www.openwall.com/lists/oss-security/2026/04/11/9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34933.json
- https://github.com/avahi/avahi/security/advisories/GHSA-w65r-6gxh-vhvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-34933
- https://github.com/avahi/avahi/commit/625ca0fac19229f6dfa3a6c6b698ae657187e50c
- https://github.com/avahi/avahi/pull/891
