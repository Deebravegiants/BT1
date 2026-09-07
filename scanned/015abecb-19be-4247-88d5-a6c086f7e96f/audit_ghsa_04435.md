# [M] Shopware: Stored XSS via SVG file upload — no SVG sanitization

## Summary
Severity: Medium
Advisory: GHSA-xvhc-gm7j-mhmc
CVE: CVE-2026-48015
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-xvhc-gm7j-mhmc
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.18
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.18

## Details
SVG files are in the `allowed_extensions` whitelist and can be uploaded by any admin user via the media manager. There is zero SVG content sanitization anywhere in the upload pipeline. A malicious SVG with JavaScript (`onload`, `<script>`, `<foreignObject>`) executes in the context of the Shopware domain when accessed.

## The Problem

In `src/Core/Framework/Resources/config/packages/shopware.yaml`, line 194:

```yaml
allowed_extensions: ["jpg", "jpeg", "png", "webp", "avif", "gif", "svg", ...]
```

SVG is whitelisted. The upload path (`MediaUploadController` → `FileSaver` → `TypeDetector`) recognizes SVG as `ImageType` with `VECTOR_GRAPHIC` flag, but no code strips JavaScript, event handlers, or external entity references from the SVG XML.

A search of the entire codebase for SVG sanitization returns — no `DOMPurify`, no `svg-sanitize`, no `strip_tags` on SVG content, nothing.

## Impact

Stored XSS affecting all users who view the uploaded SVG. In an e-commerce context, this can lead to admin account takeover, customer data theft, or malicious plugin installation.

## Suggested Fix

Either:

1. **Remove SVG from `allowed_extensions`** if SVG upload is not a core requirement
2. **Sanitize SVG content** on upload using a library like `enshrined/svg-sanitize` (strips scripts, event handlers, external references)
3. **Serve SVGs with `Content-Disposition: attachment`** to prevent inline rendering
4. **Serve SVGs from a separate domain** (like Nextcloud's `usercontent.apps.nextcloud.com`)

Option 2 is the most practical — `enshrined/svg-sanitize` is already used by WordPress and other PHP projects.

Regards & BG,
Keyvan Hardani

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-xvhc-gm7j-mhmc
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.18
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
