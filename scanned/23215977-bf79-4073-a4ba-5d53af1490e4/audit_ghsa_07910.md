# [C] Parse Server: Account takeover via JWT algorithm confusion in Google auth adapter

## Summary
Severity: Critical
Advisory: GHSA-4q3h-vp4r-prv2
CVE: CVE-2026-27804
CWE: CWE-327, CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-4q3h-vp4r-prv2
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.3.1-alpha.4
- npm: `parse-server` — affected >=0 <8.6.3

## Details
### Impact

An unauthenticated attacker can forge a Google authentication token with `alg: "none"` to log in as any user linked to a Google account, without knowing their credentials. All deployments with Google authentication enabled are affected.

### Patches

The fix hardcodes the expected `RS256` algorithm instead of trusting the JWT header, and replaces the Google adapter's custom key fetcher with `jwks-rsa` which rejects unknown key IDs.

### Workarounds

Disable Google authentication until you can upgrade.

### References

- GitHub advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-4q3h-vp4r-prv2
- Fixed in Parse Server 9.3.1-alpha.4: https://github.com/parse-community/parse-server/releases/tag/9.3.1-alpha.4
- Fixed in Parse Server 8.6.3: https://github.com/parse-community/parse-server/releases/tag/8.6.3

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-4q3h-vp4r-prv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27804
- https://github.com/parse-community/parse-server/commit/9b94083accb7f3e72c6b8126c195c7a03dd2dfd7
- https://github.com/parse-community/parse-server/commit/9d5942d50e55c822924c27b05aa98f1393e7a330
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.3
- https://github.com/parse-community/parse-server/releases/tag/9.3.1-alpha.4
