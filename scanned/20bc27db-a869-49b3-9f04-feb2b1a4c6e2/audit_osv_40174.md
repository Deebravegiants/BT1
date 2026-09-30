# [H] BetterDesk has a replay behavior vulnerability when devices are deleted

## Summary
Severity: High
Advisory: CVE-2026-50575
Aliases: GHSA-3v82-3gf8-fxx8
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50575
Type: osv

## Details
BetterDesk is a remote desktop management solution. BetterDesk versions through 2.3.0 improperly invalidate deleted device identities, allowing an unauthenticated client to replay or spoof a device ID and bypass registration controls. Version 3.0.0-alpha contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50575.json
- https://github.com/UNITRONIX/BetterDesk/security/advisories/GHSA-3v82-3gf8-fxx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-50575
- https://github.com/UNITRONIX/BetterDesk/commit/f3b4df28240694b174158335e4c0c51c8dfbe4ab
