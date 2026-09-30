# [M] Cap-go Console < 12.28.2 Account Deletion DoS via Device Identifier Association

## Summary
Severity: Medium
Advisory: CVE-2026-53982
Aliases: GHSA-qmrm-qgwr-55jf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-53982
Type: osv

## Details
Cap-go Console < 12.28.2 contains a denial-of-service vulnerability in its account deletion flow that allows an attacker to block authentication and onboarding functions by triggering account deletion while a device identifier is linked to the active session. The platform incorrectly associates the deletion state with the device identifier, causing the affected device or browser environment to be redirected to an account-disabled page for approximately 30 days, preventing any account login or registration from that device.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53982.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-qmrm-qgwr-55jf
- https://nvd.nist.gov/vuln/detail/CVE-2026-53982
- https://www.vulncheck.com/advisories/capgo-console-account-deletion-dos-via-device-identifier-association
- https://github.com/Cap-go/capgo/commit/6685e5f11adef257bf3d085e481f4d8ebcec602e
