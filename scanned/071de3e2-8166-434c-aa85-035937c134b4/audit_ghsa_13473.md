# [H] Sanitize vulnerable to Cross-site Scripting via insufficient neutralization of `style` element content

## Summary
Severity: High
Advisory: GHSA-f5ww-cq3m-q3g7
CVE: CVE-2023-36823
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-f5ww-cq3m-q3g7
Type: github-advisory

## Affected
- RubyGems: `sanitize` — affected >=3.0.0 <6.0.2

## Details
### Impact

Using carefully crafted input, an attacker may be able to sneak arbitrary HTML and CSS through Sanitize `>= 3.0.0, < 6.0.2` when Sanitize is configured to use the built-in "relaxed" config or when using a custom config that allows `style` elements and one or more CSS at-rules. This could result in XSS (cross-site scripting) or other undesired behavior when the malicious HTML and CSS are rendered in a browser.

### Patches

Sanitize `>= 6.0.2` performs additional escaping of CSS in `style` element content, which fixes this issue.

### Workarounds

Users who are unable to upgrade can prevent this issue by using a Sanitize config that doesn't allow `style` elements, using a Sanitize config that doesn't allow CSS at-rules, or by manually escaping the character sequence `</` as `<\/` in `style` element content.

### Credit

This issue was found by @cure53 during an audit of a project that uses Sanitize and was reported by one of that project's maintainers. Thank you!

## References
- https://github.com/rgrove/sanitize/security/advisories/GHSA-f5ww-cq3m-q3g7
- https://nvd.nist.gov/vuln/detail/CVE-2023-36823
- https://github.com/rgrove/sanitize/commit/76ed46e6dc70820f38efe27de8dabd54dddb5220
- https://github.com/rgrove/sanitize
- https://github.com/rgrove/sanitize/releases/tag/v6.0.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sanitize/CVE-2023-36823.yml
- https://lists.debian.org/debian-lts-announce/2023/11/msg00008.html
