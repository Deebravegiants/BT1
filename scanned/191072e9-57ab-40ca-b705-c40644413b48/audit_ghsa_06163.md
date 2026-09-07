# [M] Snipe-IT vulnerable to stored XSS via inline-served attachment

## Summary
Severity: Medium
Advisory: GHSA-jhph-5q74-pmfx
CVE: CVE-2026-55466
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-jhph-5q74-pmfx
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
A low-privilege user can store an active-content payload as an asset attachment and have it served inline, same-origin, with an active Content-Type, achieving stored XSS. The application sanitizes uploads only when PHP finfo detects image/svg+xml. By submitting an XHTML document whose finfo MIME is text/xml (an allowed extension), the svg-sanitize branch is skipped, the <script> is stored raw, and the inline-serve path returns it as text/xml; charset=utf-8 with Content-Disposition: inline — which the browser renders as a live XHTML document and executes. The dedicated StorageHelper::allowSafeInline() whitelist that should have constrained inline-renderable types is never wired into the serve path.

### Details
Vulnerable code — sanitizer keyed on finfo MIME `app/Http/Requests/UploadFileRequest.php:46-53`

```php
$extension = $file->getClientOriginalExtension();
$file_name = $name_prefix.'-'.str_random(8).'-'.str_slug(...).'.'.$file->guessExtension();
...
if ($file->getMimeType() === 'image/svg+xml') {
    $uploaded_file = $this->handleSVG($file);   // svg-sanitize fires
} else {
    $uploaded_file = file_get_contents($file);   // stored RAW — no sanitization
}
```

Vulnerable code — inline serve, no `allowSafeInline()` `app/Http/Controllers/UploadedFilesController.php:103`

```php
if (request('inline') == 'true') {
    $headers = ['Content-Disposition' => 'inline'];
    return Storage::download($path.$log->filename, $log->filename, $headers);
}
```

`StorageHelper::allowSafeInline()` (`app/Helpers/StorageHelper.php:88`) exists to whitelist inline-renderable types but is not called here. The validation rule (`UploadFileRequest::rules()`) is `mimes`: over `config('filesystems.allowed_upload_extensions_for_validator')`, which includes svg, xml, and txt — so a text/xml file passes validation and bypasses the SVG sanitizer simultaneously.

POC
1. From a fresh install, as a user with only `assets.view` + `assets.files` targeting any existing asset created by admin
2. click on the asset created by admin and upload files.
3. create a XML file with the following payload and upload it.

```xml
<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><script>alert(document.cookie)</script></head>
<body>hi</body>
</html>
```


4. Noticed that it did not receive any error and the file was uploaded.
5. Now, can just get the URL and view it. (need to add the `inline=true`).
image.png

Notice that the XSS was able to request `document.cookie`. This means that it is possible for low privilege user to perform XSS and perform privilege escalation to admin.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-jhph-5q74-pmfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55466
- https://github.com/grokability/snipe-it/commit/000cea0a622d586366cf60d2240c7c2a4b17c955
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
