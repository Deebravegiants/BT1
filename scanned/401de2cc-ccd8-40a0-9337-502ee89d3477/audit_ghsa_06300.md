# [M] phpMyFAQ has Potential Authenticated Path Traversal in PDF Export

## Summary
Severity: Medium
Advisory: GHSA-88g4-74f3-63x9
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-88g4-74f3-63x9
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=4.0.0-alpha <4.1.5
- Packagist: `phpmyfaq/phpmyfaq` — affected >=4.0.0-alpha <4.1.5

## Details
## Summary

There is an authenticated path traversal condition in the PDF export functionality, specifically within the PDF image resolution logic.

The issue may allow a privileged FAQ editor to cause the application to attempt reading files outside the intended content directory during PDF generation.

---

## Affected Component

**File:**
`src/phpMyFAQ/Export/Pdf/Wrapper.php`

**Function:**
`concatenatePaths()`

---

## Root Cause

The path resolution logic relies on locating the substring `"content"` within a user-controlled path:

```php
$pos = strpos($trimmedFile, 'content');
$relativePath = substr($trimmedFile, (int) $pos);
```

If `"content"` is not present, `strpos()` returns `false`, which becomes `0` when cast to an integer.

As a result, the entire attacker-controlled path is preserved.

Example:

```php
$trimmedFile = "../../../etc/passwd";
$pos = false;
$relativePath = "../../../etc/passwd";
```

The resulting path is later processed by:

```php
file_get_contents($resolvedPath);
```

without canonicalization or a root-directory containment check.

---

## Observed Data Flow

```text
FAQ Content
    ->
PDF Export
    ->
WriteHTML()
    ->
Wrapper::Image()
    ->
concatenatePaths()
    ->
file_get_contents()
```

---

## Potential Impact

Based on code review, a user with FAQ editing privileges may be able to store HTML containing crafted image paths that are processed during PDF generation.

Potential consequences may include:

- Path traversal outside the intended content directory
- Local file read attempts during PDF export
- Possible disclosure of readable files depending on file type, sanitization behavior, and PDF rendering constraints

---

## Discovery Method

This issue was initially detected by an internally developed SAST tool during analysis of the phpMyFAQ source code.

The finding was then manually investigated and validated through code review.

While the original scanner output classified the issue as a generic path traversal/local file inclusion pattern, manual analysis identified the specific root cause in the path resolution logic of `concatenatePaths()`.

---

## Potential Exploitation Scenario

The following scenario is based on code review and intended to illustrate the potential impact:

1. A user with FAQ editing privileges creates or modifies a FAQ entry.

2. The FAQ content contains an HTML image tag with a crafted relative path that does not include the expected `content` directory reference.

3. The HTML content is stored and later processed by the PDF export functionality.

4. When a user requests the PDF version of the FAQ, the application invokes `WriteHTML()`, which eventually reaches `Wrapper::Image()`.

5. `concatenatePaths()` constructs a filesystem path without canonicalization or directory containment validation.

6. The resulting path reaches `file_get_contents()`, causing the application to attempt reading a file outside the intended content directory.

7. Depending on sanitization behavior, file permissions, image validation, and PDF rendering behavior, the contents of the targeted file may potentially be exposed to the PDF consumer.

Based on my current analysis, exploitation would require a user capable of editing FAQ content and is therefore not considered an anonymous or unauthenticated attack vector.

---

## Suggested Remediation

Consider replacing substring-based path anchoring with:

- `realpath()` canonicalization
- Strict root-directory containment checks
- Explicit allowlisting of permitted image locations

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-88g4-74f3-63x9
- https://github.com/thorsten/phpMyFAQ/commit/91ce64405479933d7d62c751fa79c2f5c6fda591
- https://github.com/thorsten/phpMyFAQ/commit/b709ebe69405385785c2a74ae940c3e8d4cd0a8b
- https://github.com/thorsten/phpMyFAQ
