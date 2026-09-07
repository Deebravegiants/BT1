# [C] Samly access control vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h3rw-77w7-92gf
CVE: CVE-2024-25718
CWE: CWE-400, CWE-613
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-11
Source: https://github.com/advisories/GHSA-h3rw-77w7-92gf
Type: github-advisory

## Affected
- Hex: `Samly` — affected >=0 <1.4.0

## Details
In the Samly package before 1.4.0 for Elixir, `Samly.State.Store.get_assertion/3` can return an expired session, which interferes with access control because Samly.AuthHandler uses a cached session and does not replace it, even after expiry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25718
- https://github.com/dropbox/samly/pull/13
- https://github.com/dropbox/samly/pull/13/commits/812b5c3ad076dc9c9334c1a560c8e6470607d1eb
- https://github.com/dropbox/samly/commit/7637ebeef6c6b88ec2032f5323c32edcebbacbc6
- https://diff.hex.pm/diff/samly/1.3.0..1.4.0
- https://github.com/dropbox/samly
- https://github.com/handnot2/samly
- https://hex.pm/packages/samly
