# [M] Trix: Stored XSS via HTMLParser attribute injection on paste

## Summary
Severity: Medium
Advisory: GHSA-53g2-mvcc-q9x3
CVE: CVE-2026-73428
CWE: CWE-79
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-53g2-mvcc-q9x3
Type: github-advisory

## Affected
- npm: `trix` — affected >=0 <2.1.18
- RubyGems: `action_text-trix` — affected >=0 <2.1.18

## Details
### Impact

The Trix editor, in versions prior to 2.1.18, is vulnerable to XSS when crafted HTML is pasted into the editor. The `HTMLParser` processed a mock attachment, a `<span>` carrying an empty `data-trix-attachment="{}"`. The empty attachment object caused the element to bypass attachment handling, so its `data-trix-attributes` were applied to a plain string piece. The pre-2.1.18 `StringPiece.fromJSON` accepted the `href` without validation, so an attacker-supplied `javascript:` URI was carried into the document model and emitted verbatim into the serialized HTML, executing when the content was rendered and clicked.

This is a stored XSS in any application that accepts untrusted rich text through Trix and renders the serialized output to other users. Applications that apply server-side HTML sanitization, such as the Rails built-in sanitizer, are additionally protected because the payload is neutralized on save.

This vulnerability shares its fix with GHSA-53p3-c7vp-4mcc. Both are resolved by the `StringPiece.fromJSON` sanitization added in 2.1.18. This advisory covers the paste and HTMLParser entry vector, while GHSA-53p3-c7vp-4mcc covers the drag-and-drop path through the fallback Level0InputController.

### Patches

Users should upgrade to Trix editor version 2.1.18 or later.

### References

The vulnerability was responsibly reported by HackerOne researcher [newbiefromcoma](https://hackerone.com/newbiefromcoma).

## References
- https://github.com/basecamp/trix/security/advisories/GHSA-53g2-mvcc-q9x3
- https://github.com/basecamp/trix/commit/9c0a993d9fc2ffe9d56b013b030bc238f9c0557c
- https://github.com/basecamp/trix
- https://github.com/basecamp/trix/releases/tag/v2.1.18
