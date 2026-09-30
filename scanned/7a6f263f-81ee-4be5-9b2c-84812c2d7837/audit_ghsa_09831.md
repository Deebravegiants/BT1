# [H] @tinacms/graphql's Media Endpoints Can Escape the Media Root via Symlinks or Junctions

## Summary
Severity: High
Advisory: GHSA-g87c-r2jp-293w
CVE: CVE-2026-34603
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-g87c-r2jp-293w
Type: github-advisory

## Affected
- npm: `@tinacms/graphql` — affected >=0 <2.2.2

## Details
## Summary

`@tinacms/cli` recently added lexical path-traversal checks to the dev media routes, but the implementation still validates only the path string and does not resolve symlink or junction targets.

If a link already exists under the media root, Tina accepts a path like `pivot/written-from-media.txt` as "inside" the media directory and then performs real filesystem operations through that link target. This allows out-of-root media listing and write access, and the same root cause also affects delete.

## Details

The dev media handlers validate user-controlled paths with:

```ts
function resolveWithinBase(userPath: string, baseDir: string): string {
  const resolvedBase = path.resolve(baseDir);
  const resolved = path.resolve(path.join(baseDir, userPath));
  if (resolved === resolvedBase) {
    return resolvedBase;
  }
  if (resolved.startsWith(resolvedBase + path.sep)) {
    return resolved;
  }
  throw new PathTraversalError(userPath);
}

function resolveStrictlyWithinBase(userPath: string, baseDir: string): string {
  const resolvedBase = path.resolve(baseDir) + path.sep;
  const resolved = path.resolve(path.join(baseDir, userPath));
  if (!resolved.startsWith(resolvedBase)) {
    throw new PathTraversalError(userPath);
  }
  return resolved;
}
```

But the validated path is then used directly for real filesystem access:

```ts
filesStr = await fs.readdir(validatedPath);
...
await fs.ensureDir(path.dirname(saveTo));
file.pipe(fs.createWriteStream(saveTo));
...
await fs.remove(file);
```

This does not account for symlinks/junctions already present below the media root. A path such as `pivot/secret.txt` can be lexically inside the media directory while the filesystem target is outside it.

## Local Reproduction

I verified this locally with a real junction on Windows.

Test layout:

- media root: `D:\bugcrowd\tinacms\temp\junction-repro4\public\uploads`
- junction under media root: `public\uploads\pivot -> D:\bugcrowd\tinacms\temp\junction-repro4\outside`
- file outside the media root: `outside\secret.txt`

Tina's current media-path validation logic was applied and used to perform the same list/write operations the route handlers use.

Observed result:

```json
{
  "media": {
    "base": "D:\\bugcrowd\\tinacms\\temp\\junction-repro4\\public\\uploads",
    "resolvedListPath": "D:\\bugcrowd\\tinacms\\temp\\junction-repro4\\public\\uploads\\pivot",
    "listedEntries": [
      "secret.txt"
    ],
    "resolvedWritePath": "D:\\bugcrowd\\tinacms\\temp\\junction-repro4\\public\\uploads\\pivot\\written-from-media.txt",
    "outsideWriteExists": true,
    "outsideWriteContents": "MEDIA_ESCAPE"
  }
}
```

This shows the problem clearly:

- the path validator accepted `pivot`
- listing revealed a file from outside the media root
- writing to `pivot/written-from-media.txt` created `outside\written-from-media.txt`

The delete path uses the same flawed containment model and should be hardened at the same time.

## Impact

- **Out-of-root file listing** via `/media/list/...`
- **Out-of-root file write** via `/media/upload/...`
- **Likely out-of-root file delete** via `/media/...` `DELETE`, using the same path-validation gap
- **Bypass of the recent path traversal hardening** for any deployment whose media tree contains a link to another location

This is especially relevant in development and self-hosted workflows where the media directory may contain symlinks or junctions intentionally or via repository content.

## Recommended Fix

Harden media path validation with canonical filesystem checks:

1. resolve the real base path with `fs.realpath()`
2. resolve the real target path, or for writes the nearest existing parent
3. compare canonical paths rather than lexical strings
4. reject any operation that traverses through a symlink/junction to leave the real media root

`path.resolve(...).startsWith(...)` is not sufficient for filesystem security on linked paths.

## Resources

- `packages/@tinacms/cli/src/next/commands/dev-command/server/media.ts`
- `packages/@tinacms/cli/src/server/models/media.ts`
- `packages/@tinacms/cli/src/utils/path.ts`

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-g87c-r2jp-293w
- https://nvd.nist.gov/vuln/detail/CVE-2026-34603
- https://github.com/tinacms/tinacms/commit/f124eabaca10dac9a4d765c9e4135813c4830955
- https://github.com/tinacms/tinacms
