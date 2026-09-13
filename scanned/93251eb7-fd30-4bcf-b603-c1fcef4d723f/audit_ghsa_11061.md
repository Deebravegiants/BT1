# [H] AVideo has an unauthenticated decrypt oracle leaking any ciphertext

## Summary
Severity: High
Advisory: GHSA-mwjc-5j4x-r686
CVE: CVE-2026-33512
CWE: CWE-287, CWE-312, CWE-326, CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-mwjc-5j4x-r686
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary
The API plugin exposes a `decryptString` action without any authentication. Anyone can submit ciphertext and receive plaintext. Ciphertext is issued publicly (e.g., `view/url2Embed.json.php`), so any user can recover protected tokens/metadata. Severity: High.

### Details
- Entry: `plugin/API/get.json.php` is unauthenticated.
- Handler: `plugin/API/API.php` `get_api_decryptString()` (lines ~5945–5966):
  ```php
  $string = decryptString($_REQUEST['string']);
  return new ApiObject($string, empty($string));
  ```
  No APISecret or user check occurs before decrypting.
- Public ciphertext source: `view/url2Embed.json.php` returns `playLink`/`playEmbedLink` (`encryptString(json_encode(...))`) to any caller.

### PoC
1. Obtain ciphertext:
   ```
   GET /view/url2Embed.json.php?url=https://example.com/video.mp4
   ```
   Copy `playLink`.
2. Decrypt without auth:
   ```
   POST /plugin/API/get.json.php?APIName=decryptString
   Content-Type: application/x-www-form-urlencoded

   string=<playLink ciphertext>
   ```
   Response contains the plaintext JSON (videoLink, title, users_id, etc.).

### Impact
- Any encrypted payload produced by the platform can be decrypted by anyone.
- Leaks tokens/links intended to be confidential; enables replay and tampering where secrecy was assumed.

### Mitigation
- Require API secret or authenticated/authorized user for `decryptString`, or remove the endpoint.
- Prefer one-way signatures (HMAC) instead of exposing generic decryption.
- Rotate encryption keys/salts after patch to invalidate exposed ciphertexts.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-mwjc-5j4x-r686
- https://nvd.nist.gov/vuln/detail/CVE-2026-33512
- https://github.com/WWBN/AVideo/commit/3fdeecef37bb88967a02ccc9b9acc8da95de1c13
- https://github.com/WWBN/AVideo
