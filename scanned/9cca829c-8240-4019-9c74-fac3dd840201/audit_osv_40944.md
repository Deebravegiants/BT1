# [M] Capgo - Unauthorized Channel Overwrite and Ownership Takeover via POST /channel Name Collision

## Summary
Severity: Medium
Advisory: CVE-2026-56249
Aliases: GHSA-vj24-j594-3wv3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56249
Type: osv

## Details
Capgo before 12.128.2 contains an authorization bypass vulnerability in the channel creation endpoint that allows authenticated users to overwrite existing channels by reusing their names. Attackers with app.create_channel permission can exploit a logic mismatch between existence validation and upsert operations to reassign channel ownership and modify critical production channel configurations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56249.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-vj24-j594-3wv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-56249
- https://www.vulncheck.com/advisories/capgo-unauthorized-channel-overwrite-and-ownership-takeover-via-post-channel-name-collision
