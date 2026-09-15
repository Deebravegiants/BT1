# [M] Cryptomator Hub OAuth token exchange HTTP downgrade via getAuthority() scheme confusion (CVE-2026-32303 bypass)

## Summary
Severity: Medium
Advisory: CVE-2026-33472
Aliases: GHSA-9q8x-whrw-x44p
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-33472
Type: osv

## Details
Cryptomator is an open-source client-side encryption application for cloud storage. Version 1.19.1 contains a logic flaw in CheckHostTrustController.getAuthority() that allows an attacker to bypass the security fix for CVE-2026-32303. The method hardcodes the URI scheme based on port number, causing HTTPS URLs with port 80 to produce the same authority string as HTTP URLs, which defeats both the consistency check and the HTTP block validation. An attacker with write access to a cloud-synced vault.cryptomator file can craft a Hub configuration where apiBaseUrl and authEndpoint use HTTPS with port 80 to pass auto-trust validation, while tokenEndpoint uses plaintext HTTP. The vault is auto-trusted without user prompt, and a network-positioned attacker can intercept the OAuth token exchange to access the Cryptomator Hub API as the victim. This issue has been fixed in version 1.19.2.

## References
- https://github.com/cryptomator/cryptomator/releases/tag/1.19.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33472.json
- https://github.com/cryptomator/cryptomator/security/advisories/GHSA-9q8x-whrw-x44p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33472
- https://github.com/cryptomator/cryptomator/pull/4179
