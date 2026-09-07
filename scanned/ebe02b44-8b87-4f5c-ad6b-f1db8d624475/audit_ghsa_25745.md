# [H] Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') in view_component

## Summary
Severity: High
Advisory: GHSA-cm9w-c4rj-r2cf
CVE: CVE-2022-24722
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-02
Source: https://github.com/advisories/GHSA-cm9w-c4rj-r2cf
Type: github-advisory

## Affected
- RubyGems: `view_component` — affected >=2.31.0 <2.31.2
- RubyGems: `view_component` — affected >=2.32.0 <2.49.1

## Details
This is an XSS vulnerability that has the potential to impact anyone using translations with the view_component gem. Data received via user input and passed as an interpolation argument to the `translate` method is not properly sanitized before display.

Versions 2.29.1 and 2.49.1 have been released and fully mitigate the vulnerability.

Avoid passing user input to the `translate` function, or sanitize the inputs before passing them.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [github/view_component](http://github.com/github/view_component) project

## References
- https://github.com/github/view_component/security/advisories/GHSA-cm9w-c4rj-r2cf
- https://nvd.nist.gov/vuln/detail/CVE-2022-24722
- https://github.com/github/view_component/commit/3f82a6e62578ff6f361aba24a1feb2caccf83ff9
- https://github.com/github/view_component
- https://github.com/github/view_component/releases/tag/v2.31.2
- https://github.com/github/view_component/releases/tag/v2.49.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/view_component/CVE-2022-24722.yml
