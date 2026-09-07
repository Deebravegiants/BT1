# [H] Composer has a command injection via malicious perforce repository

## Summary
Severity: High
Advisory: GHSA-wg36-wvj6-r67p
CVE: CVE-2026-40176
CWE: CWE-20, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-wg36-wvj6-r67p
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=2.3.0 <2.9.6
- Packagist: `composer/composer` — affected >=1.0.0 <2.2.27

## Details
### Impact
The `Perforce::generateP4Command()` method constructed shell commands by interpolating user-supplied Perforce connection parameters (port, user, client) without proper escaping. An attacker controlling a repository configuration in a malicious composer.json declaring a Perforce VCS repository could inject arbitrary commands through these values, leading to command execution in the context of the user running Composer. Composer would execute these injected commands even if Perforce is not installed.

VCS repositories are only loaded from the root composer.json file located in the directory you execute Composer commands in and from the composer config directory (e.g. `~/.config/composer/composer.json`). So this vulnerability cannot be exploited through composer.json files of packages installed as dependencies.

You are at risk of command execution if you run Composer commands on untrusted projects with attacker supplied composer.json files, regardless of whether you or any of your dependencies use Perforce.

### Patches
Fixed in Composer 2.2.27 (2.2 LTS) and 2.9.6 (mainline)

### Workarounds
- Carefully inspect composer.json files before running Composer on them. Verify that Perforce-related fields contain valid values.
- Only run Composer commands on projects from trusted sources.

## References
- https://github.com/composer/composer/security/advisories/GHSA-wg36-wvj6-r67p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40176
- https://access.redhat.com/errata/RHSA-2026:8165
- https://access.redhat.com/security/cve/CVE-2026-40176
- https://bugzilla.redhat.com/show_bug.cgi?id=2458828
- https://github.com/FriendsOfPHP/security-advisories/blob/master/composer/composer/CVE-2026-40176.yaml
- https://github.com/composer/composer
- https://github.com/composer/composer/releases/tag/2.9.6
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40176.json
