# [C] Cross site scripting vulnerability with discussion titles

## Summary
Severity: Critical
Advisory: GHSA-7x4w-j98p-854x
CVE: CVE-2022-41938
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-7x4w-j98p-854x
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=1.5.0 <1.6.2

## Details
Flarum's page title system allowed for page titles to be converted into HTML DOM nodes when pages were rendered. The change was made after `v1.5` and was not noticed.

This allowed an attacker to inject malicious HTML markup using a discussion title input, either by creating a new discussion or renaming one. The XSS attack occurs after a visitor opens the relevant discussion page.

### Impact
All communities running Flarum from `v1.5.0` to `v1.6.1` are impacted.

### Patches
The vulnerability has been fixed and published as flarum/core `v1.6.2`. All communities running Flarum from `v1.5.0` to `v1.6.1` have to upgrade as soon as possible to v1.6.2 using:

```
composer update --prefer-dist --no-dev -a -W
```

You can then confirm you run the latest version using:

```
composer show flarum/core
```

### Workarounds
**None**

### For more information
For any questions or comments on this vulnerability please visit https://discuss.flarum.org/d/27558.

For support questions create a discussion at https://discuss.flarum.org/t/support.

A reminder that if you ever become aware of a security issue in Flarum, please report it to us privately by emailing [security@flarum.org](mailto:security@flarum.org), and we will address it promptly.

## References
- https://github.com/flarum/framework/security/advisories/GHSA-7x4w-j98p-854x
- https://nvd.nist.gov/vuln/detail/CVE-2022-41938
- https://github.com/flarum/framework/commit/690de9ce0ffe7ac4d45b73e303f44340c3433138
- https://discuss.flarum.org/d/27558
- https://github.com/flarum/framework
