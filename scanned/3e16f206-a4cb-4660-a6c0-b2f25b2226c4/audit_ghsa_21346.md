# [H] Phoenix before 1.6.14 mishandles check_origin wildcarding

## Summary
Severity: High
Advisory: GHSA-p8f7-22gq-m7j9
CVE: CVE-2022-42975
CWE: CWE-346, CWE-863
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-10-17
Source: https://github.com/advisories/GHSA-p8f7-22gq-m7j9
Type: github-advisory

## Affected
- Hex: `phoenix` — affected >=0 <1.6.14

## Details
socket/transport.ex in Phoenix before 1.6.14 mishandles check_origin wildcarding. NOTE: LiveView applications are unaffected by default because of the presence of a LiveView CSRF token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42975
- https://github.com/phoenixframework/phoenix/commit/6e7185b33a59e0b1d1c0b4223adf340a73e963ae
- https://github.com/phoenixframework/phoenix
- https://hexdocs.pm/phoenix/1.6.14/changelog.html#1-6-14-2022-10-10
