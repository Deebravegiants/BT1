# [H] symfony/ux-toolkit: Path Traversal Allows Arbitrary File Write and Read via Crafted Recipe Manifest

## Summary
Severity: High
Advisory: GHSA-p9xj-fpr2-jf2q
CVE: CVE-2026-55878
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-p9xj-fpr2-jf2q
Type: github-advisory

## Affected
- Packagist: `symfony/ux-toolkit` — affected >=2.32.0 <2.36.1
- Packagist: `symfony/ux-toolkit` — affected >=3.0.0 <3.2.0

## Details
### Description
The `ux:install` console command installs files from a recipe kit by copying paths listed in a `copy-files` map. The only guard against malicious paths was `Path::isRelative()`, which returns `true` for paths like `../../../etc`. `Path::join()` then resolves the `..` segments without complaint, so the final path can escape the intended directory entirely. A crafted or compromised kit can therefore write attacker-controlled content   to arbitrary locations on the developer's machine or CI runner.

Because the copy operation creates missing parent directories and can overwrite existing files silently (with   `--force` or in non-interactive environments), an attacker who controls a kit can overwrite files such as controllers, git hooks, or `.env` to achieve code execution. The source side of `copy-files` is symmetrically   affected, enabling local file reads outside the recipe directory.

### Resolution

The fix introduces an `Assert::pathDoesNotEscapeDirectory()` helper that rejects any `copy-files` source or destination path containing a `..` segment, regardless of whether `/` or `\` is used as the separator. This check is enforced in both `RecipeManifest` (which also guards the source Finder) and `File`. As a last line of defense, the installer re-verifies the fully resolved paths with `Path::isBasePath()` immediately before each filesystem read and write.

### Credits

Symfony would like to thank Pascal Cescon for reporting the issue and Hugo Alliaume for providing the fix.

## References
- https://github.com/symfony/ux/security/advisories/GHSA-p9xj-fpr2-jf2q
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-toolkit/CVE-2026-55878.yaml
- https://github.com/symfony/ux
