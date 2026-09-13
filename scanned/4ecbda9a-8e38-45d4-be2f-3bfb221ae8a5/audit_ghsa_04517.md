# [H] statping-ng allows attackers to escalate privileges to Administrator and access sensitive components

## Summary
Severity: High
Advisory: GHSA-5442-mh7f-72px
CVE: CVE-2026-50884
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-5442-mh7f-72px
Type: github-advisory

## Affected
- Go: `github.com/statping-ng/statping-ng` — affected >=0

## Details
Incorrect access control in statping-ng v0.93.0 allows attackers to escalate privileges to Administrator and access sensitive components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50884
- https://gist.github.com/pyuysig/72acb62a9973fa394581f662c0f12704
- https://github.com/statping-ng/statping-ng
