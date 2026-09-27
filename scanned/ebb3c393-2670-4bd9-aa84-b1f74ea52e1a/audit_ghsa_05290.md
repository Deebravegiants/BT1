# [M] NocoDB: User Enumeration via Sign-In Timing

## Summary
Severity: Medium
Advisory: GHSA-jr54-jwhj-55gp
CVE: CVE-2026-47380
CWE: CWE-208, CWE-307
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-jr54-jwhj-55gp
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.04.1

## Details
### Summary
Sign-in response timing differed between known and unknown email addresses because
the unknown-user branch returned without performing a password hash comparison.

### Details
The unknown-user branch in `auth.service.ts` now performs a `bcrypt.compare` against
a fixed dummy hash so the response time of failed sign-ins is approximately
independent of whether the address exists. Rate limiting on the sign-in endpoint is
implemented in the Enterprise build only and is not affected by this advisory.

### Impact
A network-positioned attacker could enumerate registered email addresses by timing
sign-in responses. Exploitation requires only the ability to send unauthenticated
sign-in requests.

### Credit
This issue was reported by [@AndyAnh174](https://github.com/AndyAnh174).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-jr54-jwhj-55gp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47380
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.04.1
