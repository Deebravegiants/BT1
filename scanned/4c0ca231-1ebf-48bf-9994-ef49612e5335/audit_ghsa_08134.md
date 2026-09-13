# [H] Arbitrary File Read/Write via Hardlink Target Escape Through Symlink Chain in node-tar Extraction

## Summary
Severity: High
Advisory: GHSA-83g3-92jg-28cx
CVE: CVE-2026-26960
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-83g3-92jg-28cx
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.8

## Details
### Summary
`tar.extract()` in Node `tar` allows an attacker-controlled archive to create a hardlink inside the extraction directory that points to a file outside the extraction root, using default options.

This enables **arbitrary file read and write** as the extracting user (no root, no chmod, no `preservePaths`).

Severity is high because the primitive bypasses path protections and turns archive extraction into a direct filesystem access primitive.

### Details
The bypass chain uses two symlinks plus one hardlink:

1. `a/b/c/up -> ../..`
2. `a/b/escape -> c/up/../..`
3. `exfil` (hardlink) -> `a/b/escape/<target-relative-to-parent-of-extract>`

Why this works:

- Linkpath checks are string-based and do not resolve symlinks on disk for hardlink target safety.
  - See `STRIPABSOLUTEPATH` logic in:
    - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:255`
    - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:268`
    - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:281`

- Hardlink extraction resolves target as `path.resolve(cwd, entry.linkpath)` and then calls `fs.link(target, destination)`.
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:566`
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:567`
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:703`

- Parent directory safety checks (`mkdir` + symlink detection) are applied to the destination path of the extracted entry, not to the resolved hardlink target path.
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:617`
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/unpack.js:619`
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/mkdir.js:27`
  - `../tar-audit-setuid - CVE/node_modules/tar/dist/commonjs/mkdir.js:101`

As a result, `exfil` is created inside extraction root but linked to an external file. The PoC confirms shared inode and successful read+write via `exfil`.

### PoC
[hardlink.js](https://github.com/user-attachments/files/25240082/hardlink.js)
Environment used for validation:

- Node: `v25.4.0`
- tar: `7.5.7`
- OS: macOS Darwin 25.2.0
- Extract options: defaults (`tar.extract({ file, cwd })`)

Steps:

1. Prepare/locate a `tar` module. If `require('tar')` is not available locally, set `TAR_MODULE` to an absolute path to a tar package directory.

2. Run:

```bash
TAR_MODULE="$(cd '../tar-audit-setuid - CVE/node_modules/tar' && pwd)" node hardlink.js
```

3. Expected vulnerable output (key lines):

```text
same_inode=true
read_ok=true
write_ok=true
result=VULNERABLE
```

Interpretation:

- `same_inode=true`: extracted `exfil` and external secret are the same file object.
- `read_ok=true`: reading `exfil` leaks external content.
- `write_ok=true`: writing `exfil` modifies external file.

### Impact
Vulnerability type:

- Arbitrary file read/write via archive extraction path confusion and link resolution.

Who is impacted:

- Any application/service that extracts attacker-controlled tar archives with Node `tar` defaults.
- Impact scope is the privileges of the extracting process user.

Potential outcomes:

- Read sensitive files reachable by the process user.
- Overwrite writable files outside extraction root.
- Escalate impact depending on deployment context (keys, configs, scripts, app data).

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-83g3-92jg-28cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-26960
- https://github.com/isaacs/node-tar/commit/2cb1120bcefe28d7ecc719b41441ade59c52e384
- https://github.com/isaacs/node-tar/commit/d18e4e1f846f4ddddc153b0f536a19c050e7499f
- https://github.com/isaacs/node-tar
