# [H] @tinacms/graphql's `FilesystemBridge` Path Validation Can Be Bypassed via Symlinks or Junctions

## Summary
Severity: High
Advisory: GHSA-g9c2-gf25-3x67
CVE: CVE-2026-34604
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-g9c2-gf25-3x67
Type: github-advisory

## Affected
- npm: `@tinacms/graphql` — affected >=0 <2.2.2

## Details
## Summary

`@tinacms/graphql` uses string-based path containment checks in `FilesystemBridge`:

- `path.resolve(path.join(baseDir, filepath))`
- `startsWith(resolvedBase + path.sep)`

That blocks plain `../` traversal, but it does not resolve symlink or junction targets. If a symlink/junction already exists under the allowed content root, a path like `content/posts/pivot/owned.md` is still considered "inside" the base even though the real filesystem target can be outside it.

As a result, `FilesystemBridge.get()`, `put()`, `delete()`, and `glob()` can operate on files outside the intended root.

## Details

The current bridge validation is:

```ts
function assertWithinBase(filepath: string, baseDir: string): string {
  const resolvedBase = path.resolve(baseDir);
  const resolved = path.resolve(path.join(baseDir, filepath));
  if (
    resolved !== resolvedBase &&
    !resolved.startsWith(resolvedBase + path.sep)
  ) {
    throw new Error(
      `Path traversal detected: "${filepath}" escapes the base directory`
    );
  }
  return resolved;
}
```

But the bridge then performs real filesystem I/O on the resulting path:

```ts
public async get(filepath: string) {
  const resolved = assertWithinBase(filepath, this.outputPath);
  return (await fs.readFile(resolved)).toString();
}

public async put(filepath: string, data: string, basePathOverride?: string) {
  const basePath = basePathOverride || this.outputPath;
  const resolved = assertWithinBase(filepath, basePath);
  await fs.outputFile(resolved, data);
}

public async delete(filepath: string) {
  const resolved = assertWithinBase(filepath, this.outputPath);
  await fs.remove(resolved);
}
```

This is a classic realpath gap:

1. validation checks the lexical path string
2. the filesystem follows the link target during I/O
3. the actual target can be outside the intended root

This is reachable from Tina's GraphQL/local database flow. The resolver builds a validated path from user-controlled `relativePath`, but that validation is also string-based:

```ts
const realPath = path.join(collection.path, relativePath);
this.validatePath(realPath, collection, relativePath);
```

Database write and delete operations then call the bridge:

```ts
await this.bridge.put(normalizedPath, stringifiedFile);
...
await this.bridge.delete(normalizedPath);
```

## Local Reproduction

This was verified llocally with a real junction on Windows, which exercises the same failure mode as a symlink on Unix-like systems.

Test layout:

- content root: `D:\bugcrowd\tinacms\temp\junction-repro4`
- allowed collection path: `content/posts`
- junction inside collection: `content/posts/pivot -> D:\bugcrowd\tinacms\temp\junction-repro4\outside`
- file outside content root: `outside\secret.txt`

Tina's current path-validation logic was applied and used to perform bridge-style read/write operations through the junction.

Observed result:

```json
{
  "graphqlBridge": {
    "collectionPath": "content/posts",
    "requestedRelativePath": "pivot/owned.md",
    "validatedRealPath": "content\\posts\\pivot\\owned.md",
    "bridgeResolvedPath": "D:\\bugcrowd\\tinacms\\temp\\junction-repro4\\content\\posts\\pivot\\owned.md",
    "bridgeRead": "TOP_SECRET_FROM_OUTSIDE\\r\\n",
    "outsideGraphqlWriteExists": true,
    "outsideGraphqlWriteContents": "GRAPHQL_ESCAPE"
  }
}
```

That is the critical point:

- the path was accepted as inside `content/posts`
- the bridge read `outside\secret.txt`
- the bridge wrote `outside\owned.md`

So the current containment check does not actually constrain filesystem access to the configured content root once a link exists inside that tree.

## Impact

- **Arbitrary file read/write outside the configured content root**
- **Potential delete outside the configured content root** via the same `assertWithinBase()` gap in `delete()`
- **Breaks the assumptions of the recent path-traversal fixes** because only lexical traversal is blocked
- **Practical attack chains** where the content tree contains a committed symlink/junction, or an attacker can cause one to exist before issuing GraphQL/content operations

The exact network exploitability depends on how the application exposes Tina's GraphQL/content operations, but the underlying bridge bug is real and independently security-relevant.

## Recommended Fix

The containment check needs to compare canonical filesystem paths, not just string-normalized paths.

For example:

1. resolve the base with `fs.realpath()`
2. resolve the candidate path's parent with `fs.realpath()`
3. reject any request whose real target path escapes the real base
4. for write operations, carefully canonicalize the nearest existing parent directory before creating the final file

In short: use realpath-aware containment checks for every filesystem sink, not `path.resolve(...).startsWith(...)` alone.

## Resources

- `packages/@tinacms/graphql/src/database/bridge/filesystem.ts`
- `packages/@tinacms/graphql/src/database/index.ts`
- `packages/@tinacms/graphql/src/resolver/index.ts`

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-g9c2-gf25-3x67
- https://nvd.nist.gov/vuln/detail/CVE-2026-34604
- https://github.com/tinacms/tinacms/commit/f124eabaca10dac9a4d765c9e4135813c4830955
- https://github.com/tinacms/tinacms
