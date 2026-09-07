# [H] Express XSS Sanitizer: allowedTags/allowedAttributes bypass leads to permissive sanitization (XSS risk)

## Summary
Severity: High
Advisory: GHSA-3843-rr4g-m8jq
CVE: CVE-2026-33979
CWE: CWE-183, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3843-rr4g-m8jq
Type: github-advisory

## Affected
- npm: `express-xss-sanitizer` — affected >=0 <2.0.2

## Details
## Description
A vulnerability has been identified in express-xss-sanitizer (<= 2.0.1) where restrictive sanitization configurations are silently ignored.

When a developer explicitly sets:

  allowedTags: []
  allowedAttributes: {}

the library incorrectly treats these values as "not provided" due to length/emptiness checks, and falls back to sanitize-html's default configuration.

As a result, instead of stripping all HTML tags and attributes, the sanitizer allows a permissive set of tags ``` (e.g., <a>, <p>, <div>, etc.) and attributes (e.g., href on <a>)```.

This behavior violates the expected API contract and may lead to security issues such as content injection or XSS, depending on how the sanitized output is used.

##  Impact

Developers intending to fully strip HTML content by providing empty allowedTags or allowedAttributes configurations may unknowingly allow a wide range of HTML elements and attributes.

This can result in:
- Injection of unintended HTML content ```(e.g., <div>, <table>, headings)```
- Injection of links via``` <a href="...">```
- Potential XSS vectors depending on downstream usage

The impact depends on how the sanitized output is rendered or consumed, but the root issue is a mismatch between developer intent and actual behavior.

## Proof of Concept

```javascript
const { sanitize } = require('express-xss-sanitizer');
const sanitizeHtml = require('sanitize-html');

const input = '<a href="http://evil.com">click</a><p>phish</p>';

// Using express-xss-sanitizer (v2.0.1)
sanitize(input, { allowedTags: [], allowedAttributes: {} });
// => '<a href="http://evil.com">click</a><p>phish</p>'

// Expected behavior (sanitize-html directly)
sanitizeHtml(input, { allowedTags: [], allowedAttributes: {} });
// => 'clickphish'
```

## Root Cause
The issue was caused by validation logic that checked for non-empty arrays/objects:

- allowedTags required length > 0
- allowedAttributes required Object.keys(...).length > 0

This caused empty configurations ([]) and ({}) to be ignored, resulting in fallback to default permissive settings.

## Fix
The validation logic has been updated to respect explicitly provided empty configurations.

Now, if allowedTags or allowedAttributes are provided (even if empty), they are passed directly to sanitize-html without being overridden.

## References
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/security/advisories/GHSA-3843-rr4g-m8jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33979
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/commit/5623009ef11dcf095c163a38dea07b9cc22ad19f
- https://github.com/AhmedAdelFahim/express-xss-sanitizer
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/releases/tag/v2.0.2
