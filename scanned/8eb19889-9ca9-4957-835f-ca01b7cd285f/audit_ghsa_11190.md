# [M] AVideo has SSRF Protection Bypass via HTTP Redirect in Image Download Endpoints

## Summary
Severity: Medium
Advisory: GHSA-f359-r3pv-2phf
CVE: CVE-2026-33766
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-f359-r3pv-2phf
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`isSSRFSafeURL()` validates URLs against private/reserved IP ranges before fetching, but `url_get_contents()` follows HTTP redirects without re-validating the redirect target. An attacker can bypass SSRF protection by redirecting from a public URL to an internal target.

## Root Cause

**Check-time:** `isSSRFSafeURL()` at `objects/functions.php:4066` resolves the hostname and validates the IP.

**Use-time:** `url_get_contents()` at `objects/functions.php:1990` calls `file_get_contents()` with PHP's default `follow_location=1` — redirects are followed without re-validation. The wget fallback at line 2047 also follows redirects by default.

**Affected endpoint:** `objects/aVideoEncoderReceiveImage.json.php` at lines 67-68, 107-108, 135-136, 160-161:
```php
if (isValidURL($_REQUEST['downloadURL_image']) && isSSRFSafeURL($_REQUEST['downloadURL_image'])) {
    $content = url_get_contents($_REQUEST['downloadURL_image']);
```

## Proof of Concept

1. Attacker sets up `https://attacker.com/redir` to respond with `302 Location: http://169.254.169.254/latest/meta-data/`
2. Authenticated user (with upload+edit permissions) triggers image download:
```
GET /objects/aVideoEncoderReceiveImage.json.php?downloadURL_image=https://attacker.com/redir&...
```
3. `isSSRFSafeURL()` resolves `attacker.com` → public IP → passes validation
4. `url_get_contents()` follows 302 redirect to `169.254.169.254` → SSRF

## Impact

- Cloud metadata access (AWS IMDSv1, GCP, Azure)
- Internal network service access
- Bypasses the existing SSRF protection that was added to prevent exactly this class of attack

## Note

The curl path in `url_get_contents()` does NOT set `CURLOPT_FOLLOWLOCATION` so it is not affected. Only the `file_get_contents` and `wget` fallback paths are vulnerable.

## Suggested Fix

Set `follow_location` to `0` in the stream context and handle redirects manually with re-validation, or add `isSSRFSafeURL()` check inside `url_get_contents()` after resolving the final URL.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-f359-r3pv-2phf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33766
- https://github.com/WWBN/AVideo/commit/8b7e9dad359d5fac69e0cbbb370250e0b284bc12
- https://github.com/WWBN/AVideo
