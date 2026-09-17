# [H] Atlantis Workspace Handling has Path Traversal that Allows Out-of-Bounds Directory Deletion/Creation

## Summary
Severity: High
Advisory: GHSA-26w5-6g95-gj28
CVE: CVE-2026-64679
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-26w5-6g95-gj28
Type: github-advisory

## Affected
- Go: `github.com/runatlantis/atlantis` — affected >=0.19.8 <0.45.0

## Details
### Summary
Atlantis versions `>= 0.19.8` and `< 0.45.0` did not consistently validate user-controlled `workspace` values before using them to construct local workspace paths.

A crafted workspace value containing path traversal segments could cause Atlantis to resolve workspace paths outside the intended per-pull workspace directory. In vulnerable versions or code paths, Atlantis could create, use, or remove/recreate out-of-bounds directories with the privileges of the Atlantis process user, before Terraform rejected the invalid workspace name.

The issue is fixed in Atlantis `0.45.0`.

### Details
The issue is a path traversal vulnerability in Atlantis workspace handling. `workspace` values can be supplied through repository-level `atlantis.yaml` configuration accepted by the server or through authenticated API input. A value such as `../../../../../../../../tmp/f1-canary` could escape the intended Atlantis workspace root.

In affected code paths, Atlantis used the resolved workspace path for local working-directory operations. For example, workspace values were joined into repo pull paths, and clone preparation paths could call directory removal/recreation operations such as `os.RemoveAll` and `os.MkdirAll` on the resolved directory.

### PoC
In a local PoC using repo-level `atlantis.yaml`, the following workspace value caused Atlantis to resolve and use `/tmp/f1-canary` outside `~/.atlantis/repos/...`:

```yaml
version: 3
projects:
  - dir: .
    workspace: ../../../../../../../../tmp/f1-canary
```

Atlantis logs showed the out-of-bounds directory being created and Terraform being run with `/tmp/f1-canary` as the working directory. Terraform rejected the workspace name only after Atlantis had already used the out-of-bounds path.

### Impact
A user who can cause Atlantis to process a crafted `workspace` value, for example through repository-level `atlantis.yaml` configuration accepted by the server or an authenticated `/api/plan` request, may cause filesystem operations to occur outside the intended workspace boundary.

Depending on the affected version, code path, deployment configuration, and filesystem permissions, this may result in unintended directory creation, deletion, or reuse, integrity impact to writable local paths, or denial of service. Containerized deployments may limit host impact, but writable mounted volumes and persistent Atlantis data paths remain relevant.

## References
- https://github.com/runatlantis/atlantis/security/advisories/GHSA-26w5-6g95-gj28
- https://github.com/runatlantis/atlantis/pull/6254
- https://github.com/runatlantis/atlantis/commit/ea4e4ceebf8b387d015fff7ed8a7fcca33279afe
- https://github.com/runatlantis/atlantis
- https://github.com/runatlantis/atlantis/releases/tag/v0.45.0
