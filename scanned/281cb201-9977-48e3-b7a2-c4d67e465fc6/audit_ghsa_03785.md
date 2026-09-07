# [M] Moderate severity vulnerability that affects league/commonmark

## Summary
Severity: Medium
Advisory: GHSA-3v43-877x-qgmq
CVE: CVE-2019-10010
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-09-17
Source: https://github.com/advisories/GHSA-3v43-877x-qgmq
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=0 <0.18.3

## Details
## CVE-2019-10010

### Impact

In `league/commonmark` 0.18.2 and below, malicious users can insert double-encoded HTML entities into their Markdown like this:

```md
[XSS](javascript&amp;colon;alert%28&#039;XSS&#039;%29)
```

This library would (correctly) unescape the `&amp;` entity to `&` during the parsing step.  However, **the renderer step would fail to properly re-escape the resulting `&colon;` string**, thus producing the following malicious HTML output:

```html
<p><a href="javascript&colon;alert('XSS')">XSS</a></p>
```

Browsers would interpret `&colon;` as a `:` character and allow the JS to be executed when the link is clicked.

This vulnerability was present in the upstream library this project was forked from and therefore exists in all prior versions of `league/commonmark`.

### Solution

The new [0.18.3](https://github.com/thephpleague/commonmark/releases/tag/0.18.3) release mirrors [the fix made upstream](https://github.com/commonmark/commonmark.js/commit/c89b35c5fc99bdf1d2181f7f0c9fcb8a1abc27c8) - we no longer attempt to preserve entities when rendering HTML attributes like `href`, `src`, `title`, etc.

The `$preserveEntities` parameter of `Xml::escape()` is therefore no longer used internally, so it has been deprecated and marked for removal in the next major release (0.19.0).

### Credits

 - Mohit Fawaz for identifying the issue
 - Sebastiaan Knijnenburg and Ross Tuck for responsibly disclosing/relaying the issue
 - John MacFarlane for investigating it and implementing the upstream fix we mirrored here

### References

 - https://nvd.nist.gov/vuln/detail/CVE-2019-10010
 - https://github.com/thephpleague/commonmark/releases/tag/0.18.3
 - https://github.com/thephpleague/commonmark/issues/353
- https://github.com/FriendsOfPHP/security-advisories/blob/master/league/commonmark/CVE-2019-10010.yaml

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-3v43-877x-qgmq
- https://nvd.nist.gov/vuln/detail/CVE-2019-10010
- https://github.com/thephpleague/commonmark/issues/353
- https://github.com/FriendsOfPHP/security-advisories/blob/master/league/commonmark/CVE-2019-10010.yaml
- https://github.com/advisories/GHSA-3v43-877x-qgmq
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/0.18.3
