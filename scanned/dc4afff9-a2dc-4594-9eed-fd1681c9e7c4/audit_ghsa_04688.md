# [M] NocoDB: Plaintext Password Comparison in Shared Views

## Summary
Severity: Medium
Advisory: GHSA-qhxg-623c-cfjm
CVE: CVE-2026-47379
CWE: CWE-200, CWE-203
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-qhxg-623c-cfjm
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
The shared-view password check fell back to strict-equality (`===`) comparison for
legacy plaintext passwords, leaking the password's length and per-character prefix
through response timing.

### Details
The bcrypt branch (hashes starting with `$2a$`/`$2b$`) was unaffected. The legacy
fallback in `View.ts` now uses `crypto.timingSafeEqual` and a same-length dummy
compare on the length-mismatch path, so total comparison time is approximately
length-independent. The EE dashboard model's `verifyPassword` is patched the same way.

### Impact
A network-positioned attacker could mount a timing oracle against shared views whose
passwords predated the bcrypt migration. Exploitation requires the ability to time
shared-view authentication responses but no prior authentication.

### Credit
This issue was reported by [@Proscan-one](https://github.com/Proscan-one).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-qhxg-623c-cfjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-47379
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
