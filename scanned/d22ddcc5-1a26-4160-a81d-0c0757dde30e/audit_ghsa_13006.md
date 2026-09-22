# [H] pnpm incorrectly parses tar archives relative to specification

## Summary
Severity: High
Advisory: GHSA-5r98-f33j-g8h7
CVE: CVE-2023-37478
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-5r98-f33j-g8h7
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <7.33.4
- npm: `@pnpm/exe` — affected >=0 <7.33.4
- npm: `@pnpm/linux-arm64` — affected >=0 <7.33.4
- npm: `@pnpm/linux-x64` — affected >=0 <7.33.4
- npm: `@pnpm/linuxstatic-arm64` — affected >=0 <7.33.4
- npm: `@pnpm/macos-arm64` — affected >=0 <7.33.4
- npm: `@pnpm/macos-x64` — affected >=0 <7.33.4
- npm: `@pnpm/win-x64` — affected >=0 <7.33.4
- npm: `@pnpm/cafs` — affected >=0 <7.0.5
- npm: `pnpm` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/exe` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/linux-arm64` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/linux-x64` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/linuxstatic-arm64` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/macos-arm64` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/macos-x64` — affected >=8.0.0 <8.6.8
- npm: `@pnpm/win-x64` — affected >=8.0.0 <8.6.8

## Details
### Summary
It is possible to construct a tarball that, when installed via npm or parsed by the registry is safe, but when installed via pnpm is malicious, due to how pnpm parses tar archives.

### Details
The TAR format is an append-only archive format, and as such, the specification for how to update a file is to add a new record to the end with the updated version of the file. This means that it is completely valid for an archive to contain multiple copies of, say, `package.json`, and the expected behavior when extracting is that all versions other than the last get ignored.

This is further complicated by that during tarball extraction, all package managers are configured to drop the first path component, so collisions can be created simply by using multiple root folders in the archive, even without performing updates.

When pnpm extracts a tar archive via tar-stream, it appears to extract only the _first_ file of a given name and discards all subsequent files with the same name.

### PoC
Create a root folder with the following layout:
- `a/package.json`
- `package/package.json`
- `z/package.json`

File contents:
#### a/package.json
```json
{
    "name": "test-package",
    "version": "0.1.0",
    "description": "This is a bad version of a test package",
    "dependencies": {
        "react": "^15"
    }
}
```
#### package/package.json
```json
{
    "name": "test-package",
    "version": "0.1.0",
    "description": "This is a bad version of a test package",
    "dependencies": {
        "react": "^16"
    }
}
```
#### z/package.json
```json
{
    "name": "test-package",
    "version": "0.1.0",
    "description": "This is the good version of a test package",
    "dependencies": {
        "react": "^17"
    }
}
```

Then use the tar binary to produce a tarball (working directory is the root folder):
`tar -c -z --format ustar -f package.tgz a package z`
The order of the folders at the end matters; whichever one is last will end up being the package.json that wins when extracted by npm; the one that is first will be the one that wins when extracted by pnpm.

Install the tarball via the `file:` protocol.

Observe that with npm, the lockfile has `react@17`, while with pnpm it has `react@15`.

### Impact
This can result in a package that appears safe on the npm registry or when installed via npm being replaced with a compromised or malicious version when installed via pnpm.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-5r98-f33j-g8h7
- https://nvd.nist.gov/vuln/detail/CVE-2023-37478
- https://github.com/pnpm/pnpm
- https://github.com/pnpm/pnpm/releases/tag/v7.33.4
- https://github.com/pnpm/pnpm/releases/tag/v8.6.8
