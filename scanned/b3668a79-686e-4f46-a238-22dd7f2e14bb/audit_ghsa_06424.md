# [M] humanfs: Recursive copy follows symlinked files and copies data from outside the source tree

## Summary
Severity: Medium
Advisory: GHSA-p498-v437-472g
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-p498-v437-472g
Type: github-advisory

## Affected
- npm: `@humanfs/node` — affected >=0 <0.16.8

## Details
### Summary

`@humanfs/node` does not treat symlinks as a separate case during copy operations. A symlink placed inside an attacker-controlled source tree can make `copyAll()` read and copy the contents of any file readable by the process, even when that file is outside the directory being copied.

### Details

The Node implementation exposes symlink state through `list()`, but `copyAll()` ignores it. During recursive copies, every non-directory entry is passed to `copy()`, which delegates to `fs.promises.copyFile()`.

On Node, `copyFile()` dereferences symlinks. As a result, a symlink inside the copied tree is handled as if it were an ordinary file, and the destination receives the contents of the symlink target rather than a copy of the link itself.

That breaks the expected boundary of a directory copy. A caller can point `copyAll()` at a seemingly self-contained directory and still end up copying data from elsewhere on the host filesystem if the source tree contains attacker-supplied symlinks.

The same dereference behavior also affects `copy()` when the source path itself is a symlink.

### PoC

```js
import { NodeHfs } from "@humanfs/node";
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";

const root = await fs.mkdtemp(path.join(os.tmpdir(), "humanfs-"));
const src = path.join(root, "src");
const dst = path.join(root, "dst");
const secret = path.join(root, "secret.txt");

await fs.mkdir(src);
await fs.writeFile(secret, "TOPSECRET");
await fs.symlink(secret, path.join(src, "link.txt"));

const hfs = new NodeHfs();
await hfs.copyAll(src, dst);

console.log(await fs.readFile(path.join(dst, "link.txt"), "utf8"));
// TOPSECRET
```

### Impact

If an application uses `copyAll()` or `copy()` on attacker-controlled paths, a symlink can be used to pull arbitrary readable host files into the copied output. In practice, that can turn a normal workspace copy, export, or packaging step into a file disclosure primitive.

## References
- https://github.com/humanwhocodes/humanfs/security/advisories/GHSA-p498-v437-472g
- https://github.com/humanwhocodes/humanfs/commit/22bbaa4487a3e6c1197ca619840de4615d0c3404
- https://github.com/humanwhocodes/humanfs
- https://github.com/humanwhocodes/humanfs/releases/tag/node-v0.16.8
