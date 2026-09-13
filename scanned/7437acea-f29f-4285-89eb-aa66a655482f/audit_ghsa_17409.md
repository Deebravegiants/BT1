# [H] Parse Server is vulnerable to Server-Side Request Forgery (SSRF) via Instagram OAuth Adapter

## Summary
Severity: High
Advisory: GHSA-3f5f-xgrj-97pf
CVE: CVE-2025-68150
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-12-16
Source: https://github.com/advisories/GHSA-3f5f-xgrj-97pf
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.1.1-alpha.1
- npm: `parse-server` — affected >=0 <8.6.2

## Details
## Impact

The Instagram authentication adapter allows clients to specify a custom API URL via the `apiURL` parameter in `authData`. This enables SSRF attacks and possibly authentication bypass if malicious endpoints return fake responses to validate unauthorized users.

## Patches

Fixed by hardcoding the Instagram Graph API URL `https://graph.instagram.com` and ignoring client-provided `apiURL` values.

## Workarounds

None.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-3f5f-xgrj-97pf
- https://nvd.nist.gov/vuln/detail/CVE-2025-68150
- https://github.com/parse-community/parse-server/pull/9988
- https://github.com/parse-community/parse-server/pull/9989
- https://github.com/parse-community/parse-server
