# [H] Possible cross-site scripting attack via unsanitized SVG files in FoF Upload

## Summary
Severity: High
Advisory: GHSA-fm53-mpmp-7qw2
CVE: CVE-2022-30999
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-fm53-mpmp-7qw2
Type: github-advisory

## Affected
- Packagist: `fof/upload` — affected >=0 <1.2.3

## Details
### Impact
If FoF Upload is configured to allow the uploading of SVG files (`image/svg+xml`), navigating directly to an SVG file URI could execute arbitrary Javascript code decided by an attacker.

This Javascript code could include the execution of HTTP web requests to Flarum, or any other web service. This could allow data to be leaked by an authenticated Flarum user, or, possibly, for data to be modified maliciously.

### Patches
This has been patched with v1.2.3, which now sanitizes uploaded SVG files.

### Workarounds
Upgrade to `1.2.3` (requires Flarum 1.2 or later), or remove the ability for users to upload SVG files through FoF Upload.

### References
Thank you to Safwat Refaat for the responsible disclosure of this vulnerability.

## References
- https://github.com/FriendsOfFlarum/upload/security/advisories/GHSA-fm53-mpmp-7qw2
- https://nvd.nist.gov/vuln/detail/CVE-2022-30999
- https://github.com/FriendsOfFlarum/upload/issues/68
- https://github.com/FriendsOfFlarum/upload/pull/318
- https://github.com/FriendsOfFlarum/upload
- https://github.com/FriendsOfFlarum/upload/releases/tag/1.2.3
