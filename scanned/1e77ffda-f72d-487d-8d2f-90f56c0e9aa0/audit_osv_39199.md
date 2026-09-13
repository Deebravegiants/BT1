# [H] FileRise: TOTP Bypass via Setup Endpoint Disclosing Existing Secret

## Summary
Severity: High
Advisory: CVE-2026-44460
Aliases: GHSA-84hw-8g73-v3f8
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44460
Type: osv

## Details
FileRise is a self-hosted web-based file manager with multi-file upload, editing, and batch operations. Prior to 3.12.0, /api/totp_setup.php is callable from a session that has only passed the password check (state pending_login_user). When the target account already has TOTP configured, the endpoint decrypts and returns the user's existing TOTP secret inside the QR PNG instead of refusing or generating a new secret. An attacker who already possesses the victim's password can therefore retrieve the live TOTP secret, derive a valid one-time code, submit it to /api/totp_verify.php, and obtain a fully authenticated session without ever possessing the victim's authenticator device. This vulnerability is fixed in 3.12.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44460.json
- https://github.com/error311/FileRise/security/advisories/GHSA-84hw-8g73-v3f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44460
