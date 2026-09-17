# [H] FileRise: Default Encryption Key Enables Token Forgery and Config Decryption

## Summary
Severity: High
Advisory: CVE-2026-33072
Aliases: GHSA-f4xx-57cv-mg3x
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33072
Type: osv

## Details
FileRise is a self-hosted web file manager / WebDAV server. In versions prior to 3.9.0, a hardcoded default encryption key (default_please_change_this_key) is used for all cryptographic operations — HMAC token generation, AES config encryption, and session tokens — allowing any unauthenticated attacker to forge upload tokens for arbitrary file upload to shared folders, and to decrypt admin configuration secrets including OIDC client secrets and SMTP passwords. FileRise uses a single key (PERSISTENT_TOKENS_KEY) for all crypto operations. The default value default_please_change_this_key is hardcoded in two places and used unless the deployer explicitly overrides the environment variable. This issue is fixed in version 3.9.0.

## References
- https://github.com/error311/FileRise/releases/tag/v3.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33072.json
- https://github.com/error311/FileRise/security/advisories/GHSA-f4xx-57cv-mg3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33072
