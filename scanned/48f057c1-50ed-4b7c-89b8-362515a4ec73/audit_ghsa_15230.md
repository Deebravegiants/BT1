# [M] Flarum's logout Route allows open redirects

## Summary
Severity: Medium
Advisory: GHSA-733r-8xcp-w9mr
CVE: CVE-2024-21641
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-05
Source: https://github.com/advisories/GHSA-733r-8xcp-w9mr
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=0 <1.8.5
- Packagist: `flarum/framework` — affected >=0 <1.8.5

## Details
### Impact
The Flarum `/logout` route includes a redirect parameter that allows any third party to redirect users from a (trusted) domain of the Flarum installation to redirect to any link. Sample: `example.com/logout?return=https://google.com`. For logged-in users, the logout must be confirmed. Guests are immediately redirected. This could be used by spammers to redirect to a web address using a trusted domain of a running Flarum installation.

Some ecosystem extensions modifying the logout route have already been affected. Sample: https://discuss.flarum.org/d/22229-premium-wordpress-integration/526

### Patches
The vulnerability has been fixed and published as flarum/core v1.8.5. All communities running Flarum should upgrade as soon as possible to v1.8.5 using:

`composer update --prefer-dist --no-dev -a -W`

You can then confirm you run the latest version using:

`composer show flarum/core`

### Workarounds
Some extensions modifying the logout route can remedy this issue if their implementation is safe. In any case we recommend updating to 1.8.5.

### References
For any questions or comments on this vulnerability, please visit https://discuss.flarum.org/

For support questions, create a discussion at https://discuss.flarum.org/t/support.

A reminder that if you ever become aware of a security issue in Flarum, please report it to us privately by emailing [security@flarum.org](mailto:security@flarum.org), and we will address it promptly.

## References
- https://github.com/flarum/framework/security/advisories/GHSA-733r-8xcp-w9mr
- https://nvd.nist.gov/vuln/detail/CVE-2024-21641
- https://github.com/flarum/flarum-core/commit/ee8b3b4ad1413a2b0971fdd9e40f812d2a3a9d3a
- https://github.com/flarum/framework/commit/7d70328471cf3091d92d95c382d277aec7996176
