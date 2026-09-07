# [M] Older releases of better_errors open to Cross-Site Request Forgery attack

## Summary
Severity: Medium
Advisory: GHSA-w3j4-76qw-wwjm
CVE: CVE-2021-39197
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-w3j4-76qw-wwjm
Type: github-advisory

## Affected
- RubyGems: `better_errors` — affected >=0 <2.8.0

## Details
### Impact
better_errors prior to 2.8.0 did not implement CSRF protection for its internal requests. It also did not enforce the correct "Content-Type" header for these requests, which allowed a cross-origin "simple request" to be made without CORS protection. These together left an application with better_errors enabled open to cross-origin attacks.

_As a developer tool, better_errors documentation strongly recommends addition only to the `development` bundle group, so this vulnerability should only affect development environments. Please ensure that your project limits better_errors to the `development` group (or the non-Rails equivalent)._

### Patches
Starting with release 2.8.x, CSRF protection is enforced. It is recommended that you upgrade to the latest release, or minimally to "~> 2.8.3".

### Workarounds
There are no known workarounds to mitigate the risk of using older releases of better_errors.

### References
- Chris Moberly provided [an example attack that uses a now-patched vulnerability of webpack-dev-server in conjunction with Better Errors](https://about.gitlab.com/blog/2021/09/07/why-are-developers-vulnerable-to-driveby-attacks/)

### For more information
If you have any questions or comments about this advisory, please
- Add to the [discussion in better_errors](https://github.com/BetterErrors/better_errors/discussions/507)
- Open an issue in [better_errors](https://github.com/BetterErrors/better_errors)

## References
- https://github.com/BetterErrors/better_errors/security/advisories/GHSA-w3j4-76qw-wwjm
- https://nvd.nist.gov/vuln/detail/CVE-2021-39197
- https://github.com/BetterErrors/better_errors/pull/474
- https://github.com/BetterErrors/better_errors/commit/8e8e796bfbde4aa088741823c8a3fc6df2089bb0
- https://github.com/BetterErrors/better_errors
- https://github.com/BetterErrors/better_errors/discussions/507
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/better_errors/CVE-2021-39197.yml
