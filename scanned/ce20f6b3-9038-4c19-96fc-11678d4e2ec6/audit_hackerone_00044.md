# [H] Path traversal by monkey-patching Buffer internals

## Summary
Severity: High
Program: Internet Bug Bounty
Weakness: Path Traversal
Reporter: tniessen
State: resolved
Disclosed: 2024-05-29T14:32:15.660Z
CVE: CVE-2024-21896
Source: https://hackerone.com/reports/2434811

## Details
**Summary:** In Node.js 20 and Node.js 21, the permission model protects itself against path traversal attacks by calling `path.resolve()` on any paths given by the user. If the path is to be treated as a `Buffer`, the implementation uses `Buffer.from()` to obtain a `Buffer` from the result of `path.resolve()`. By monkey-patching `Buffer` internals, namely, `Buffer.prototype.utf8Write`, the application can modify the result of `path.resolve()`, which leads to a path traversal vulnerability.

**Description:** This vulnerability was introduced in [commit 1f64147e](https://github.com/nodejs/node/commit/1f64147eb607f82060e08884f993597774c69280), which itself was a patch of a path traversal vulnerability (see CVE-2023-32004, [report 2038134](https://hackerone.com/reports/2038134)). Subsequent commits made the implementation more resilient against monkey-patching, for example, by not allowing users to replace `path.resolve()` ([commit 32bcf4ca](https://github.com/nodejs/node/commit/32bcf4ca27bba9d4e48418f12dc6d7c2252e71ec)) or `Buffer.from()` ([commit f447a461](https://github.com/nodejs/node/commit/f447a4611a49d1843c17bf9ffbc86a835f1f1b9c)) with user-defined functions. Nevertheless, the internals of `Buffer.from` can be monkey-patched in multiple ways. Most importantly, overwriting `Buffer.prototype.utf8Write` with a user-defined function enables a straightforward path traversal vulnerability because virtually any sanitization performed by `path.resolve()` can be overridden by the user.

## Steps to reproduce:

This can be exploited simply by overwriting `Buffer.prototype.utf8Write` with a user-defined function. The code is supposed to only have access to `/tmp`, yet it successfully reads `/etc/passwd`.

```
$ node --experimental-permission --allow-fs-read=/tmp 
Welcome to Node.js v20.8.1.
Type ".help" for more information.
> Buffer.prototype.utf8Write = ((w) => function (str, ...args) {
...   return w.apply(this, [str.replace(/^\/exploit/, '/tmp/..'), ...args]);
... })(Buffer.prototype.utf8Write);
[Function (anonymous)]
> fs.readFileSync(new TextEncoder().encode('/exploit/etc/passwd'))
<Buffer 72 6f 6f 74 3a 78 3a 30 3a 30 3a 72 6f 6f 74 3a 2f 72 6f 6f 74 3a 2f 62 69 6e 2f 62 61 73 68 0a 64 61 65 6d 6f 6e 3a 78 3a 31 3a 31 3a 64 61 65 6d 6f ... 3174 more bytes>
```

This example pretends to attempt to read `/exploit/etc/passwd`, which would ultimately be denied. However, after the permission model implementation has called `path.resolve()`, the exploit intercepts the internal call to `utf8Write()` within `Buffer.from()` and replaces the sanitized path with `/tmp/../etc/passwd`, thus bypassing the path traversal protection logic. Because Node.js assumes that the path has been resolved at this point, it allows access because the path begins with `/tmp/`.

## Suggested minimal patch:

```patch
diff --git a/lib/internal/fs/utils.js b/lib/internal/fs/utils.js
index 611b6c2420..d7e6ec3aa2 100644
--- a/lib/internal/fs/utils.js
+++ b/lib/internal/fs/utils.js
@@ -66,4 +66,6 @@ const kStats = Symbol('stats');
 const assert = require('internal/assert');
 
+const { encodeUtf8String } = internalBinding('encoding_binding');
+
 const {
   fs: {
@@ -720,5 +722,8 @@ function possiblyTransformPath(path) {
     assert(isUint8Array(path));
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2434811_
