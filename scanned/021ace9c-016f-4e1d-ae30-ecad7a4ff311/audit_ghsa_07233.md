# [C] Decompress: Archive extraction can create files and links outside of the target directory

## Summary
Severity: Critical
Advisory: GHSA-mp2f-45pm-3cg9
CVE: CVE-2026-53486
CWE: CWE-22, CWE-59, CWE-732
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-mp2f-45pm-3cg9
Type: github-advisory

## Affected
- npm: `@xhmikosr/decompress` — affected >=0 <10.2.1
- npm: `@xhmikosr/decompress` — affected >=11.0.0 <11.1.3
- npm: `decompress` — affected >=0

## Details
### Impact

When extracting an archive to a directory, a crafted archive can read or write files outside that directory. The flaw is in the code that writes the parsed entries, so it affects every format decompress handles: tar, tar.gz, tar.bz2, and zip by default, plus any others added through the plugins option.

A link (hardlink) or symlink entry is created without checking where its target points. A hardlink can be aimed at any file the running process can read; that file then appears inside the output directory and its contents are exposed. A symlink can point outside the output directory and redirect a later write.

The path containment check used a string prefix comparison (`realPath.indexOf(outputPath) !== 0`). Output `/srv/out` does not contain `/srv/out-old`, but the prefix comparison treats it as inside, so an entry can escape into a sibling directory whose name starts with the output directory name.

File modes were applied as `mode & ~umask`, which does not remove the setuid, setgid, or sticky bits. A crafted entry can create a setuid or setgid file. This matters when extraction runs as root, for example in CI, containers, or install scripts.

Any code that extracts archives from an untrusted or attacker-influenced source is affected. Archives are commonly downloaded before extraction, so this is reachable over the network in many setups.

### Patches

Fixed in `@xhmikosr/decompress` 10.2.1 and 11.1.3. Link targets are now resolved and checked against the output directory, containment uses `path.relative`, and setuid, setgid, and sticky bits are removed.

The upstream `decompress` package is unmaintained, and all versions through its last release (4.2.1) have the same flaws. There is no upstream fix. Migrate to `@xhmikosr/decompress` 11.1.3 or later.

### Workarounds

Extract only archives you trust. Run extraction as a non-root user so the mode issue cannot create a privileged file. After extracting, reject any symlink or hardlink that points outside the target and any file with unexpected mode bits.

### Resources

* Related prior issue in the upstream project this package forks: CVE-2020-12265 / GHSA-qgfr-5hqp-vrw9
* Fix commits and releases:
  * https://github.com/XhmikosR/decompress/releases/tag/v10.2.1
  * https://github.com/XhmikosR/decompress/releases/tag/v11.1.3
  * https://github.com/XhmikosR/decompress/commit/aca5aac
  * https://github.com/XhmikosR/decompress/commit/281cefa
  * https://github.com/XhmikosR/decompress/commit/60b5299

## References
- https://github.com/XhmikosR/decompress/security/advisories/GHSA-mp2f-45pm-3cg9
- https://github.com/XhmikosR/decompress/commit/281cefa
- https://github.com/XhmikosR/decompress/commit/60b5299
- https://github.com/XhmikosR/decompress/commit/aca5aac
- https://github.com/XhmikosR/decompress
