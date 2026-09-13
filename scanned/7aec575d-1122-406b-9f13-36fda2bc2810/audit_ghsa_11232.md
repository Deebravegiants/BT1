# [C] @siteboon/claude-code-ui is Vulnerable to Command Injection via Multiple Parameters

## Summary
Severity: Critical
Advisory: GHSA-f2fc-vc88-6w7q
CVE: CVE-2026-31862
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-f2fc-vc88-6w7q
Type: github-advisory

## Affected
- npm: `@siteboon/claudecodeui` — affected >=0 <1.24.0

## Details
### Summary
Multiple Git-related API endpoints use execAsync() with string interpolation of user-controlled parameters (file, branch, message, commit), allowing authenticated attackers to execute arbitrary OS commands.

### Details
The claudecodeui application provides Git integration through various API endpoints. These endpoints accept user-controlled parameters such as file paths, branch names, commit messages, and commit hashes, which are directly interpolated into shell command strings passed to execAsync().

The application attempts to escape double quotes in some parameters, but this protection is trivially bypassable using other shell metacharacters such as:

Command substitution: $(command) or \`command\`
Command chaining: ;, &&, ||
Newlines and other control characters

### Affected Endpoints
`GET /api/git/diff - file parameter`
`GET /api/git/status - file parameter`
`POST /api/git/commit - files array and message parameter`
`POST /api/git/checkout - branch parameter`
`POST /api/git/create-branch - branch parameter`
`GET /api/git/commits - commit hash parameter`
`GET /api/git/commit-diff - commit parameter`

### Vulnerable Code

File: server/routes/git.js
```
// Line 205 - git status with file parameter
const { stdout: statusOutput } = await execAsync(
  `git status --porcelain "${file}"`,  // INJECTION via file
  { cwd: projectPath }
);
```
```
// Lines 375-379 - git commit with files array and message
for (const file of files) {
  await execAsync(`git add "${file}"`, { cwd: projectPath });  // INJECTION via files[]
}
const { stdout } = await execAsync(
  `git commit -m "${message.replace(/"/g, '\\"')}"`,  // INJECTION via message (bypass with $())
  { cwd: projectPath }
);
```
```
// Lines 541-543 - git show with commit parameter (no quotes!)
const { stdout } = await execAsync(
  `git show ${commit}`,  // INJECTION via commit
  { cwd: projectPath }
);
```

### Impact
- Remote Code Execution as the Node.js process user
- Full server compromise
- Data exfiltration
- Supply chain attacks - modify committed code to inject malware

---

### Fix

**Commit:** siteboon/claudecodeui@55567f4

#### Root cause remediation

All vulnerable `execAsync()` calls have been replaced with the existing `spawnAsync()` helper (which uses `child_process.spawn` with `shell: false`). Arguments are passed as an array directly to the OS — shell metacharacters in user input are inert.

**Endpoints patched in `server/routes/git.js`:**

- `GET /api/git/diff` — `file` (4 calls)
- `GET /api/git/file-with-diff` — `file` (3 calls)
- `POST /api/git/commit` — `files[]`, `message`
- `POST /api/git/checkout` — `branch`
- `POST /api/git/create-branch` — `branch`
- `GET /api/git/commits` — `commit.hash`
- `GET /api/git/commit-diff` — `commit`
- `POST /api/git/generate-commit-message` — `file`
- `POST /api/git/discard` — `file` (3 calls)
- `POST /api/git/delete-untracked` — `file`
- `POST /api/git/publish` — `branch`

A strict allowlist regex (`/^[0-9a-f]{4,64}$/i`) was also added to validate the `commit` parameter in `/api/git/commit-diff` before it reaches the git process.

#### Before / After

```js
// BEFORE — shell interprets the string, injection possible
const { stdout } = await execAsync(`git show ${commit}`, { cwd: projectPath });

// AFTER — no shell, args passed directly to the process
const { stdout } = await spawnAsync('git', ['show', commit], { cwd: projectPath });
```

## References
- https://github.com/siteboon/claudecodeui/security/advisories/GHSA-f2fc-vc88-6w7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-31862
- https://github.com/siteboon/claudecodeui
- https://github.com/siteboon/claudecodeui/releases/tag/v1.24.0
