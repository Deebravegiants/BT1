# [H] Arbitrary HTML present after sanitization because of unicode normalization

## Summary
Severity: High
Advisory: GHSA-wvhx-q427-fgh3
CVE: CVE-2024-34078
Ecosystem: PyPI
Published: 2024-05-06
Source: https://github.com/advisories/GHSA-wvhx-q427-fgh3
Type: github-advisory

## Affected
- PyPI: `html-sanitizer` — affected >=0 <2.4.2

## Details
### Impact

If using `keep_typographic_whitespace=False` (which is the default), the sanitizer normalizes unicode to the NFKC form at the end. Some unicode characters normalize to chevrons; this allows specially crafted HTML to escape sanitization.

### Patches

The problem has been fixed in 2.4.2.

### Workarounds

Set `keep_typographic_whitespace=True` explicitly, or normalize to NFKC yourself earlier.

## References
- https://github.com/matthiask/html-sanitizer/security/advisories/GHSA-wvhx-q427-fgh3
- https://github.com/matthiask/html-sanitizer/commit/48db42fc5143d0140c32d929c46b802f96913550
- https://github.com/matthiask/html-sanitizer
