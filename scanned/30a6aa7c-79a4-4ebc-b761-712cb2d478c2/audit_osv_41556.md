# [H] OpenClaw < 2026.6.9 Symlink Following via Mirror Sync

## Summary
Severity: High
Advisory: CVE-2026-62189
Aliases: GHSA-m38g-vpwj-mpg9
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62189
Type: osv

## Details
OpenClaw versions before 2026.6.9 contain a symlink following vulnerability in the mirror sync feature that allows lower-trust callers to perform actions requiring stronger authorization. Attackers can exploit remote symlink parents to bypass policy checks and authorization boundaries when the feature is enabled and reachable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62189.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m38g-vpwj-mpg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-62189
- https://www.vulncheck.com/advisories/openclaw-symlink-following-via-mirror-sync
- https://github.com/openclaw/openclaw
