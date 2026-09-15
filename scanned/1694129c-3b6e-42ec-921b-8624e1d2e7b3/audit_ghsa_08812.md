# [M] Grav is Vulnerable to XXE via SVG Upload 

## Summary
Severity: Medium
Advisory: GHSA-3446-6mgw-f79p
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3446-6mgw-f79p
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
Dear Grav Security Team,

A security vulnerability was discovered in Grav CMS that allows authenticated attackers to read arbitrary files from the server through XML External Entity (XXE) injection.

 Vulnerability Summary

| Field | Details |
|-------|---------|
| Vulnerability Type | XML External Entity (XXE) Injection |
| Severity | High (CVSS 7.5) |
| Affected Versions | Grav CMS <= 1.7.x |
| Affected Component | SVG file upload/processing |
| CWE | CWE-611: Improper Restriction of XML External Entity Reference |
| Authentication Required | Yes (Admin panel access) |

Technical Details

 Root Cause
The application uses `simplexml_load_string()` to process uploaded SVG files without disabling external entity loading. This allows attackers to inject XXE payloads that are processed by the XML parser.

 Vulnerable Code Pattern
```php
// Current (Vulnerable):
$svg = simplexml_load_string($content);

// No LIBXML_NOENT flag or entity loader protection
```

 Attack Vector
1. Attacker authenticates to Grav admin panel
2. Uploads malicious SVG file via Pages → Media or File Manager plugin
3. Server parses SVG and processes XXE entities
4. Arbitrary file contents are exfiltrated

 Impact

An authenticated attacker can:

1. Read sensitive files:
   - `/etc/passwd` - System user information
   - `user/accounts/*.yaml` - Admin credentials and 2FA secrets
   - `user/config/system.yaml` - System configuration
   - `.env` files - Environment secrets and API keys

2. Perform SSRF - Access internal services via external entity URLs

3. Potential DoS - Billion laughs attack via recursive entity expansion

Proof of Concept

 Malicious SVG Payload
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <text x="10" y="50">&xxe;</text>
</svg>
```

 Steps to Reproduce
1. Login to Grav CMS admin panel
2. Navigate to Pages → select any page → Media tab
3. Upload the malicious SVG file
4. Observe file contents in response/error or stored output

 Recommended Fix

 Option 1: Add XXE Protection Flags
```php
libxml_use_internal_errors(true);
$svg = simplexml_load_string($content, 'SimpleXMLElement', LIBXML_NOENT | LIBXML_DTDLOAD);
```

 Option 2: Use SVG Sanitizer Library (Recommended)
```php
use enshrined\svgSanitize\Sanitizer;

$sanitizer = new Sanitizer();
$sanitizer->removeRemoteReferences(true);
$cleanSVG = $sanitizer->sanitize($content);
```

The `enshrined/svg-sanitize` library properly strips XXE payloads and other malicious SVG content.

 Request

1. Please acknowledge receipt of this report within 5 business days
2. Please provide an estimated timeline for a security patch
3. I am happy to assist with testing the fix
4. I request a CVE be assigned for this vulnerability
5. If you have a security advisory process, please include me in the credits

Turki Almatrafi.



---

## Maintainer note — fix applied (2026-04-24)

Fixed across two repos:

1. **Grav core on the `2.0` branch** (commit [`5a12f9be8`](https://github.com/getgrav/grav/commit/5a12f9be8), ships in **2.0.0-beta.2**) — `VectorImageMedium::__construct` (the code path that reads width/height from an uploaded SVG) now strips `<!DOCTYPE>` and `<!ENTITY>` declarations before parsing, and calls `simplexml_load_string` with `LIBXML_NONET | LIBXML_NOERROR | LIBXML_NOWARNING`. On PHP < 8 it also calls `libxml_disable_entity_loader(true)` for the duration of the parse.

2. **rhukster/dom-sanitizer** (commit [`02d08ec`](https://github.com/rhukster/dom-sanitizer/commit/02d08ec)) — the library Grav ships as its SVG sanitizer. `loadDocument` now applies the same DOCTYPE/ENTITY strip and passes `LIBXML_NONET` to `loadXML`/`loadHTML`.

With both layers in place, the PoC:

```xml
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <text x="10" y="50">&xxe;</text>
</svg>
```

no longer expands `&xxe;`, and the parser cannot make outbound filesystem or network requests for external entities/DTDs. Billion-laughs-style entity expansion is also neutralized because the declarations are stripped before libxml ever sees them.

**Files:**
- [`system/src/Grav/Common/Page/Medium/VectorImageMedium.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Page/Medium/VectorImageMedium.php).
- [`tests/unit/Grav/Common/Security/SvgXxeSecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/SvgXxeSecurityTest.php) — XXE neutralization + billion-laughs + plain-SVG regression.
- dom-sanitizer: [`src/DOMSanitizer.php`](https://github.com/rhukster/dom-sanitizer/blob/main/src/DOMSanitizer.php) + two new XXE tests in its own suite.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-3446-6mgw-f79p
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
