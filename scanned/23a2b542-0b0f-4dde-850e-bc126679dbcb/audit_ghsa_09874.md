# [M] coursevault-preview has a path traversal due to improper base-directory boundary validation

## Summary
Severity: Medium
Advisory: GHSA-9h9m-rr67-9jpg
CVE: CVE-2026-35613
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-9h9m-rr67-9jpg
Type: github-advisory

## Affected
- npm: `coursevault-preview` — affected >=0 <0.1.1

## Details
## Summary

`coursevault-preview` versions prior to `0.1.1` contain a path traversal vulnerability in the `resolveSafe` utility. The boundary check used `String.prototype.startsWith(baseDir)` on a normalized path, which does not enforce a directory boundary. An attacker who controls the `relativePath` argument to affected `CoursevaultPreview` methods may be able to read files outside the configured `baseDir` when a sibling directory exists whose name shares the same string prefix.

## Details

The vulnerable code in `src/utils/errors.ts`:

```ts
if (!full.startsWith(base)) {   // ← insufficient
  throw new Error("Path escapes the base directory");
}
```

Because the check is a raw string prefix test rather than a path-boundary test, the following bypass is possible:

```
baseDir  = "/srv/courses"
payload  = "../courses-admin/config.json"
resolved = "/srv/courses-admin/config.json"

"/srv/courses-admin/config.json".startsWith("/srv/courses") // → true ✗
```

Any file whose absolute path begins with the `baseDir` string — including files in sibling directories that share a name prefix — passes the guard and can be accessed by the caller through affected file-access methods.

The fix replaces the check with a separator-aware comparison:

```ts
if (full !== base && !full.startsWith(base + sep)) {
  throw new Error("Path escapes the base directory");
}
```

## Impact

An application that passes untrusted input as the `relativePath` argument to affected file-access methods may expose file contents outside the intended directory.

1. Attacker control over the `relativePath` parameter.
2. A sibling directory on the filesystem whose name shares a string prefix with `baseDir`.

There is no network exposure in the package itself; impact is limited to local file disclosure within the host process's file system permissions.

## References
- https://github.com/moritzmyrz/coursevault-preview/security/advisories/GHSA-9h9m-rr67-9jpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35613
- https://github.com/moritzmyrz/coursevault-preview
