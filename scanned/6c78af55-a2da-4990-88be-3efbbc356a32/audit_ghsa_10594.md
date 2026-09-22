# [H] Composer has a command injection via malicious perforce reference

## Summary
Severity: High
Advisory: GHSA-gqw4-4w2p-838q
CVE: CVE-2026-40261
CWE: CWE-20, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-gqw4-4w2p-838q
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=2.3.0 <2.9.6
- Packagist: `composer/composer` — affected >=1.0.0 <2.2.27

## Details
### Impact
The `Perforce::syncCodeBase()` method appended the `$sourceReference` parameter to a shell command without proper escaping, allowing an attacker to inject arbitrary commands through a crafted source reference containing shell metacharacters. Further as in GHSA-wg36-wvj6-r67p / CVE-2026-40176 the `Perforce::generateP4Command()` method constructed shell commands by interpolating user-supplied Perforce connection parameters (port, user, client) without proper escaping from the source url field. Composer would execute these injected commands even if Perforce is not installed.

The source reference and url are provided as part of package metadata. Any Composer package repository can serve package metadata declaring perforce as a source type with a malicious source reference or source url. This means the vulnerability can be exploited through any package served by a compromised or malicious Composer repository. An attack does not require Perforce to be installed on the client, as Composer will attempt to execute the constructed command regardless.

This vulnerability is exploitable when installing or updating dependencies from source (`--prefer-source`, default when installing dev prefixed versions), even if you do not use Perforce.

### Patches
Fixed in Composer 2.2.27 (2.2 LTS) and 2.9.6 (mainline)

Note, the fix for the source url in the `Perforce::generateP4Command()` was addressed as part of the patches for GHSA-wg36-wvj6-r67p / CVE-2026-40176 in the same versions.

### Workarounds

- Avoid installing dependencies from source by using `--prefer-dist` or the `preferred-install: dist` config setting.
- Only use trusted Composer repositories.

## References
- https://github.com/composer/composer/security/advisories/GHSA-gqw4-4w2p-838q
- https://nvd.nist.gov/vuln/detail/CVE-2026-40261
- https://access.redhat.com/errata/RHSA-2026:8165
- https://access.redhat.com/security/cve/CVE-2026-40261
- https://bugzilla.redhat.com/show_bug.cgi?id=2458841
- https://github.com/FriendsOfPHP/security-advisories/blob/master/composer/composer/CVE-2026-40261.yaml
- https://github.com/composer/composer
- https://github.com/composer/composer/releases/tag/2.9.6
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40261.json
