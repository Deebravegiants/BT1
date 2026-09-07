# [M] Rails HTML Sanitizers: Possible XSS vulnerability with certain configurations

## Summary
Severity: Medium
Advisory: GHSA-cj75-f6xr-r4g7
CVE: CVE-2026-73648
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-cj75-f6xr-r4g7
Type: github-advisory

## Affected
- RubyGems: `rails-html-sanitizer` — affected >=1.0.3 <1.7.1

## Details
## Summary

There is a possible cross-site scripting vulnerability in rails-html-sanitizer when the sanitizer is configured to allow an SVG reference element such as `<use>`. See related [GHSA-9wjq-cp2p-hrgf](https://github.com/flavorjones/loofah/security/advisories/GHSA-9wjq-cp2p-hrgf) in Loofah, whose SVG local-reference logic rails-html-sanitizer mirrors.

- Versions affected: `>= 1.0.3, < 1.7.1`
- Not affected: `< 1.0.3`
- Fixed versions: `1.7.1`

## Impact

`Rails::HTML::PermitScrubber` restricts SVG reference elements in the `SVG_ALLOW_LOCAL_HREF` collection to local, same-document references, but that restriction covered only the `xlink:href` attribute. Browsers also accept a plain `href` attribute per the SVG 2 spec, and it was not restricted, so those elements could reference arbitrary external documents. SVG `<use>` can load and render external SVG content by reference, and if the referenced document is same-origin and contains scripts, it could execute in the context of the sanitized document. `<feImage>` can load external images, which can be used for tracking.

Applications are impacted only when the allowed tags are overridden to include one of these SVG reference elements, for example `<use>` or `<feImage>`. The default allowed tags do not include these SVG elements, so applications using the default configuration are not affected.

## Workarounds

Remove the SVG reference elements (such as `use` and `feImage`) from the overridden allowed tags. Applications using the default allowed tags are not affected.

## References

- [GHSA-9wjq-cp2p-hrgf: SVG `href` attribute bypasses local-reference restriction in Loofah](https://github.com/flavorjones/loofah/security/advisories/GHSA-9wjq-cp2p-hrgf)
- [CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')](https://cwe.mitre.org/data/definitions/79.html)

## Credit

Found by maintainer Mike Dalessio during a security audit.

## References
- https://github.com/rails/rails-html-sanitizer/security/advisories/GHSA-cj75-f6xr-r4g7
- https://github.com/rails/rails-html-sanitizer/commit/74dcb8053e6da9921246ce71b06ad9fd65b19586
- https://github.com/rails/rails-html-sanitizer
- https://github.com/rails/rails-html-sanitizer/releases/tag/v1.7.1
