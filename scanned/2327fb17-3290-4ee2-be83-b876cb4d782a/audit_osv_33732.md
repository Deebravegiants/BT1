# [C] CryptPad 2FA Bypass Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-49591
Aliases: GHSA-xq5x-wgcm-3p33
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-49591
Type: osv

## Details
CryptPad is a collaboration suite. Prior to version 2025.3.0, enforcement of Two-Factor Authentication (2FA) in CryptPad can be trivially bypassed, due to weak implementation of access controls. An attacker that compromises a user's credentials can gain access to the victim's account, even if the victim has 2FA set up. This is due to 2FA not being enforced if the path parameter is not 44 characters long, which can be bypassed by simply URL encoding a single character in the path. This issue has been patched in version 2025.3.0.

## References
- https://github.com/cryptpad/cryptpad/blob/15c81aa8ccb737a9a1167481f4a699af331364bb/lib/http-worker.js#L356-L364
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49591.json
- https://github.com/cryptpad/cryptpad/security/advisories/GHSA-xq5x-wgcm-3p33
- https://nvd.nist.gov/vuln/detail/CVE-2025-49591
- https://github.com/cryptpad/cryptpad/commit/0c5d4bbf5e5206d53470ea86a664fa2b703fb611
- https://github.com/cryptpad/cryptpad/commit/f624f9d457d36040f57c7598d98a8b9461b79837
