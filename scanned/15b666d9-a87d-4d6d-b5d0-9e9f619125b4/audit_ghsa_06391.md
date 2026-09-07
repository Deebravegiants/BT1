# [M] Sulu: Stored XSS via media download inline-disposition override

## Summary
Severity: Medium
Advisory: GHSA-pp4x-ccxq-6r33
CVE: CVE-2026-82396
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-pp4x-ccxq-6r33
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=0 <2.6.25
- Packagist: `sulu/sulu` — affected >=3.0.0-alpha1 <3.0.8

## Details
### Impact

Stored Cross Site Scripting (XSS) in the media download endpoint.

The download route (`/media/{id}/download/{slug}` and its admin variant) accepts the query parameter `?inline=1`. When it is present, the response is sent with the header `Content-Disposition: inline` for any MIME type, which overrides the disposition rules the server would otherwise apply. By default, HTML and other scriptable uploads are not blocked, the file is served on the application origin with its stored `Content-Type`, and no `X-Content-Type-Options` or `Content-Security-Policy` header is sent. Because of this, an attacker can upload an HTML file and build a link that runs their own JavaScript in the context of the Sulu origin.

Every installation where users who are not fully trusted can upload media is affected. This includes editors who hold the media add permission. Such an editor can store a payload that runs in the authenticated session of anyone who opens the link, including an administrator, which allows theft of the session and credentials and lets the attacker act as the victim.

The problem is present on the 2.6 and 3.0 branches and goes back to the introduction of the `?inline` override in 2017. It is not the same as CVE-2024-47617, which was a reflected XSS through the `slug` and is already fixed.

### Patches

Fixed in **2.6.25** and **3.0.8**. The download route now forces `Content-Disposition: attachment` for MIME types a browser renders as a document (`text/html`, `application/xhtml+xml`, `text/xml`, `application/xml`), even when `?inline=1` is requested. Inline viewing is unchanged for safe types such as PDF and images.

### Workarounds

Block scriptable uploads by MIME type through `sulu_media.upload.blocked_file_types`. This stops new uploads only, so existing media has to be reviewed separately.

```yaml
sulu_media:
    upload:
        blocked_file_types: [text/html, application/xhtml+xml, image/svg+xml, text/xml, application/xml, text/javascript, application/javascript]
```

At the web server or reverse proxy, force `Content-Disposition: attachment` and add `X-Content-Type-Options: nosniff` and a restrictive `Content-Security-Policy` on the paths `/media/*/download/*` and `/admin/media/*/download/*`.

Serve uploaded media from a separate origin that does not share the application cookies.

Restrict the media upload permission to trusted users and keep the default SVG sanitizer enabled.

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-pp4x-ccxq-6r33
- https://nvd.nist.gov/vuln/detail/CVE-2026-82396
- https://github.com/sulu/sulu/commit/d061094f5b7bb1d5e974544fce30bede9c7adf8e
- https://github.com/sulu/sulu
- https://github.com/sulu/sulu/releases/tag/2.6.25
- https://github.com/sulu/sulu/releases/tag/3.0.8
