# [H] Parse Server's MFA recovery codes not consumed after use

## Summary
Severity: High
Advisory: GHSA-4hf6-3x24-c9m8
CVE: CVE-2026-31875
CWE: CWE-672
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-4hf6-3x24-c9m8
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.6.0-alpha.7
- npm: `parse-server` — affected >=0 <8.6.33

## Details
### Impact

When multi-factor authentication (MFA) via TOTP is enabled for a user account, Parse Server generates two single-use recovery codes. These codes are intended as a fallback when the user cannot provide a TOTP token. However, recovery codes are not consumed after use, allowing the same recovery code to be used an unlimited number of times. This defeats the single-use design of recovery codes and weakens the security of MFA-protected accounts.

An attacker who obtains a single recovery code can repeatedly authenticate as the affected user without the code ever being invalidated.

### Patches

The fix ensures that each recovery code is removed from the stored recovery code list after a successful login.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-4hf6-3x24-c9m8
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.7
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.33

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-4hf6-3x24-c9m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-31875
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.33
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.7
