# [M] Capgo - Integrity Issue in Release Routing via Multiple Public Channels

## Summary
Severity: Medium
Advisory: CVE-2026-56328
Aliases: GHSA-3cmp-pm5x-8464
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56328
Type: osv

## Details
Capgo before 12.128.2 allows multiple public channels for the same app and platform to coexist simultaneously, while unnamed /updates requests without defaultChannel implicitly resolve to a single hidden winner channel. An authorized app or channel manager can create ambiguous default update state and silently influence which bundle unnamed clients receive, breaking release routing integrity and predictability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56328.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-3cmp-pm5x-8464
- https://nvd.nist.gov/vuln/detail/CVE-2026-56328
- https://www.vulncheck.com/advisories/capgo-integrity-issue-in-release-routing-via-multiple-public-channels
