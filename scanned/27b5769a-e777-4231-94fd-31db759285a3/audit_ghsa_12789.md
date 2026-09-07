# [M] Improper neutralization of `noscript` element content may allow XSS in Sanitize

## Summary
Severity: Medium
Advisory: GHSA-fw3g-2h3j-qmm7
CVE: CVE-2023-23627
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-28
Source: https://github.com/advisories/GHSA-fw3g-2h3j-qmm7
Type: github-advisory

## Affected
- RubyGems: `sanitize` — affected >=5.0.0 <6.0.1

## Details
### Impact

Using carefully crafted input, an attacker may be able to sneak arbitrary HTML through Sanitize `>= 5.0.0, < 6.0.1` when Sanitize is configured with a custom allowlist that allows `noscript` elements. This could result in XSS (cross-site scripting) or other undesired behavior when that HTML is rendered in a browser.

Sanitize's default configs don't allow `noscript` elements and are not vulnerable. This issue only affects users who are using a custom config that adds `noscript` to the element allowlist.

### Patches

Sanitize `>= 6.0.1` always removes `noscript` elements and their contents, even when `noscript` is in the allowlist.

### Workarounds

Users who are unable to upgrade can prevent this issue by using one of Sanitize's default configs or by ensuring that their custom config does not include `noscript` in the element allowlist.

### Details

The root cause of this issue is that HTML parsing rules treat the contents of a `noscript` element differently depending on whether scripting is enabled in the user agent. Nokogiri (the HTML parser Sanitize uses) doesn't support scripting so it follows the "scripting disabled" rules, but a web browser with scripting enabled will follow the "scripting enabled" rules. This means that Sanitize can't reliably make the contents of a `noscript` element safe for scripting enabled browsers. The safest thing to do is to remove the element and its contents entirely, which is now what Sanitize does in version 6.0.1 and later.

### References

- [Release Notes](https://github.com/rgrove/sanitize/releases/tag/v6.0.1)

### Credit

Thanks to David Klein from [TU Braunschweig](https://www.tu-braunschweig.de/en/ias) (@leeN) for reporting this issue.

## References
- https://github.com/rgrove/sanitize/security/advisories/GHSA-fw3g-2h3j-qmm7
- https://nvd.nist.gov/vuln/detail/CVE-2023-23627
- https://github.com/rgrove/sanitize/commit/ec14265e530dc3fe31ce2ef773594d3a97778d22
- https://github.com/rgrove/sanitize
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sanitize/CVE-2023-23627.yml
