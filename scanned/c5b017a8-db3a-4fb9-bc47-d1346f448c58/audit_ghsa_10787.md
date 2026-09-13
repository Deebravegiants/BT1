# [C] Payload: Pre-Authentication Account Takeover via Parameter Injection in Password Recovery

## Summary
Severity: Critical
Advisory: GHSA-hp5w-3hxx-vmwf
CVE: CVE-2026-34751
CWE: CWE-472, CWE-640
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-hp5w-3hxx-vmwf
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.79.1
- npm: `@payloadcms/graphql` — affected >=0 <3.79.1

## Details
### Impact

A vulnerability in the password recovery flow could allow an unauthenticated attacker to perform actions on behalf of a user who initiates a password reset.

Users are affected if:

- They are using Payload version **< v3.79.1** with any auth-enabled collection using the built-in `forgot-password` functionality.

### Patches

Input validation and URL construction in the password recovery flow have been hardened.

Users should upgrade to **v3.79.1** or later.

### Workarounds

There are no complete workarounds. Upgrading to **v3.79.1** is recommended.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-hp5w-3hxx-vmwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34751
- https://github.com/payloadcms/payload
- https://github.com/payloadcms/payload/releases/tag/v3.79.1
