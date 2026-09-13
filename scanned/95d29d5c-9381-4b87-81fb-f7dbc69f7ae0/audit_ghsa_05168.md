# [M] Shopware: SSRF in Media External-Link Endpoint Bypasses IP Validation

## Summary
Severity: Medium
Advisory: GHSA-gq96-5pfx-f4vc
CVE: CVE-2026-48013
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-gq96-5pfx-f4vc
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1

## Details
## Summary

The `/api/_action/media/external-link` endpoint allows authenticated admin users to make server-side HTTP HEAD requests to arbitrary internal IP addresses. While the parallel `uploadFromURL` flow validates target IPs against private/reserved ranges via `FileUrlValidator`, the `linkURL` flow only performs a URL format check (regex for `http://` or `https://` prefix), allowing SSRF to internal network services and cloud metadata endpoints.

## Details

The vulnerability is an inconsistency between two URL-handling flows in `MediaUploadService`.

**Vulnerable path** (`external-link`):

`MediaUploadV2Controller::externalLink()` at `src/Core/Content/Media/Api/MediaUploadV2Controller.php:66` takes a user-supplied `url` parameter and passes it to `MediaUploadService::linkURL()` at `src/Core/Content/Media/Upload/MediaUploadService.php:134`.

`linkURL()` calls `getContentSizeFromValidExternalUrl($url)` at line 159, which only validates via `validateExternalUrl()`:

```php
// src/Core/Content/Media/Upload/MediaUploadService.php:207-212
public static function validateExternalUrl(string $url): void
{
    if (!preg_match('/^https?:\/\/.+/', $url)) {
        throw MediaException::invalidUrl($url);
    }
}
```

Then makes a server-side HEAD request with no IP filtering:

```php
// src/Core/Content/Media/Upload/MediaUploadService.php:292-300
private function getContentSizeFromValidExternalUrl(string $url): int
{
    $this->validateExternalUrl($url);

    $headers = $this->httpClient->request('HEAD', $url)->getHeaders();
    if (!\array_key_exists('content-length', $headers)) {
        throw MediaException::fileNotFound($url);
    }

    return (int) $headers['content-length'][0];
}
```

**Protected path** (`upload_by_url`):

In contrast, `uploadFromURL` uses `FileFetcher::fetchFromURL()` which calls `FileUrlValidator::isValid()`:

```php
// src/Core/Content/Media/File/FileFetcher.php:64
if ($this->enableUrlValidation && !$this->fileUrlValidator->isValid($url)) {
    throw MediaException::illegalUrl($url);
}
```

`FileUrlValidator::isValid()` resolves the hostname via `gethostbyname()` and validates the IP against private and reserved ranges using `filter_var()` with `FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE`. This protection is entirely absent from the `linkURL` flow.

## Impact

An authenticated admin user can:

1. **Probe cloud metadata services** — HEAD requests to `169.254.169.254` reveal whether cloud metadata endpoints exist and leak content-length values
2. **Scan internal networks** — Differentiate open/closed/filtered ports on internal hosts (10.x, 172.16.x, 192.168.x) based on response timing and error types
3. **Leak internal service information** — The `fileSize` field stored in the database reflects the `content-length` header from internal services
4. **Redirect-based escalation** — Symfony HttpClient follows redirects by default (max_redirects=20), allowing an attacker-controlled external server to redirect the HEAD request to arbitrary internal destinations

Impact is limited to information disclosure via HEAD requests. The admin authentication requirement (PR:H) reduces exploitability, but in multi-tenant or compromised-credential scenarios this allows network reconnaissance from the server's perspective.

## Recommended Fix

Apply `FileUrlValidator` to the `linkURL` flow, consistent with the `uploadFromURL` flow. In `MediaUploadService`:

```php
// src/Core/Content/Media/Upload/MediaUploadService.php

// Add constructor dependency:
private readonly FileUrlValidatorInterface $fileUrlValidator;

// In getContentSizeFromValidExternalUrl(), add IP validation:
private function getContentSizeFromValidExternalUrl(string $url): int
{
    $this->validateExternalUrl($url);

    if (!$this->fileUrlValidator->isValid($url)) {
        throw MediaException::illegalUrl($url);
    }

    $headers = $this->httpClient->request('HEAD', $url)->getHeaders();
    if (!\array_key_exists('content-length', $headers)) {
        throw MediaException::fileNotFound($url);
    }

    return (int) $headers['content-length'][0];
}
```

Additionally, consider setting `max_redirects: 0` on the HttpClient request to prevent redirect-based SSRF bypasses.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-gq96-5pfx-f4vc
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
