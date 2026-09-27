# [C] LazyOwn: Default C2 Operator Credentials Enable Administrative Access to C2 Dashboard

## Summary
Severity: Critical
Advisory: CVE-2026-68503
Aliases: GHSA-38jf-j9x7-jf6f
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-68503
Type: osv

## Details
LazyOwn RedTeam/APT Framework is an AI-powered C2 and red-team operations framework. Prior to 0.2.154, LazyOwn ships default C2 credentials LazyOwn and LazyOwn in payload.json and core/payload_schema.py and passes them unchanged to lazyc2.py HTTP Basic authentication, allowing any network-reachable attacker who knows the defaults to authenticate to the C2 dashboard with operator-level access. This issue is fixed in 0.2.154.

## References
- https://github.com/grisuno/LazyOwn/releases/tag/release/0.2.154
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68503.json
- https://github.com/grisuno/LazyOwn/security/advisories/GHSA-38jf-j9x7-jf6f
- https://nvd.nist.gov/vuln/detail/CVE-2026-68503
- https://github.com/grisuno/LazyOwn/commit/2e1e3a7b5da8149ae28a970b5883aefa42921652
