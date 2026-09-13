# [H] PHP_CodeSniffer gitblame report command injection via crafted filename

## Summary
Severity: High
Advisory: GHSA-hmqg-cxww-wqhq
CVE: CVE-2026-67434
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-hmqg-cxww-wqhq
Type: github-advisory

## Affected
- Packagist: `squizlabs/php_codesniffer` — affected >=0 <3.13.6
- Packagist: `squizlabs/php_codesniffer` — affected >=4.0.0 <4.0.2

## Details
### Impact

PHP_CodeSniffer versions before v3.13.6 and v4.0.2 contain a command injection vulnerability in the code creating the `Gitblame`, `Hgblame` and `Svnblame` report(s).

As a result, running PHP_CodeSniffer over untrusted files, for example, in a CI pipeline that scans pull requests, or on a developer machine reviewing third-party code, could result in attacker-controlled shell commands being executed when the `Gitblame`, `Hgblame` or `Svnblame` report(s) would process a file whose name contains shell metacharacters.

* Users using the default `Full` report, or any of the other non-*blame reports, are not affected.
* Users on a runtime platform which does not allow filenames to contain shell metacharacters, such as `"` and `;`, are not affected.

### Patched versions

The issue has been fixed in PHP_CodeSniffer v3.13.6 and v4.0.2. We recommend all users upgrade to these versions at their earliest convenience.

### Workaround

Users of PHP_CodeSniffer who cannot upgrade immediately should ensure they do not use the `Gitblame`, `Hgblame` or the `Svnblame` reports when scanning untrusted code.

This is especially relevant for CI jobs, pre-commit or review tooling, automated review services, and any service that scans untrusted repositories or uploaded source trees.

### Credits

Many thanks to both [@Faze-up](https://github.com/Faze-up) and [@edorian](https://github.com/edorian) for responsibly disclosing this vulnerability.

### How can I report a security bug?

Please report security vulnerabilities privately via [the "Security and quality" tab on the PHP_CodeSniffer repository](https://github.com/PHPCSStandards/PHP_CodeSniffer/security).

## References
- https://github.com/PHPCSStandards/PHP_CodeSniffer/security/advisories/GHSA-hmqg-cxww-wqhq
- https://github.com/PHPCSStandards/PHP_CodeSniffer/pull/1473
- https://github.com/PHPCSStandards/PHP_CodeSniffer/commit/7a3a6bbf153a03fa3a9413afc60bded6b764e76b
- https://github.com/PHPCSStandards/PHP_CodeSniffer/commit/f0e1ebb0563f0e5d7f190497a787bcaf8474f3fe
- https://github.com/FriendsOfPHP/security-advisories/blob/master/squizlabs/php_codesniffer/CVE-2026-67434.yaml
- https://github.com/PHPCSStandards/PHP_CodeSniffer
- https://github.com/PHPCSStandards/PHP_CodeSniffer/releases/tag/3.13.6
- https://github.com/PHPCSStandards/PHP_CodeSniffer/releases/tag/4.0.2
