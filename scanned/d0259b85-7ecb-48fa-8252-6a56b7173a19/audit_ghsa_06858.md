# [H] WordPress Coding Standards (WordPressCS) contains an arbitrary code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-3pwp-g2mj-5p3v
CVE: CVE-2026-45293
CWE: CWE-95
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-3pwp-g2mj-5p3v
Type: github-advisory

## Affected
- Packagist: `wp-coding-standards/wpcs` — affected >=0.14.1 <3.4.1

## Details
### Impact

WordPress Coding Standards (WordPressCS) versions before 3.4.1 contain an arbitrary code execution vulnerability in the `WordPress.WP.EnqueuedResourceParameters` sniff. As a result, running PHPCS with WordPressCS over untrusted PHP code, for example, in a CI pipeline that lints pull requests, or on a developer machine reviewing third-party code, could lead to arbitrary command execution on the scanning host.

This affects users of the `WordPress` and `WordPress-Extra` rulesets. The `WordPress-Core` ruleset and the `WordPress-Docs` ruleset are not affected.

The vulnerability happens when the sniff checks whether the `$var` argument passed to functions such as `wp_enqueue_script()` or `wp_register_script()` evaluates to a falsy value. The sniff's `is_falsy()` method reconstructed the argument and ran it through `eval()`. Because of this, a maliciously crafted `$ver` argument such as `'system'('id')` would be executed during the scan.

### Patches

This issue has been fixed in WordPressCS 3.4.1. We recommend all users upgrade to 3.4.1 or later.

### Workaround

Users of the `WordPress` and `WordPress-Extra` rulesets, who cannot upgrade immediately, can disable the affected sniff by adding an `<exclude>` tag to their custom ruleset (the `<rule>` `ref` value might vary depending on the ruleset):

```xml
<rule ref="WordPress">
	<exclude name="WordPress.WP.EnqueuedResourceParameters"/>
</rule>
```

To verify that the sniff has been disabled, run PHPCS with the `-e` flag, which lists all the sniffs a standard will run. `WordPress.WP.EnqueuedResourceParameters` should no longer appear in the output under the `WordPress` section:

```
phpcs -e --standard=/path/to/ruleset.xml
```

### Credits

Many thanks to [@FORIMOC](https://github.com/FORIMOC) for responsibly disclosing this vulnerability.

### How can I report a security bug?

Please report security vulnerabilities privately via [the "Security and quality" tab on the WPCS repository](https://github.com/WordPress/WordPress-Coding-Standards/security).

## References
- https://github.com/WordPress/WordPress-Coding-Standards/security/advisories/GHSA-3pwp-g2mj-5p3v
- https://github.com/WordPress/WordPress-Coding-Standards/pull/2771
- https://github.com/WordPress/WordPress-Coding-Standards/commit/a29048d0bbef5cf25d42349c74e4072d3cbc8325
- https://github.com/WordPress/WordPress-Coding-Standards
- https://github.com/WordPress/WordPress-Coding-Standards/releases/tag/3.4.1
