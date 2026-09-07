# [H] ZeptoClaw: Path boundary checks bypass via symlink, TOCTOU, and hardlink

## Summary
Severity: High
Advisory: GHSA-2m67-cxxq-c3h8
CVE: CVE-2026-32232
CWE: CWE-22, CWE-62
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-2m67-cxxq-c3h8
Type: github-advisory

## Affected
- crates.io: `zeptoclaw` — affected >=0 <0.7.6

## Details
### Summary
Workspace boundary enforcement currently has three related bypass risks. This issue tracks fixing all three in one pull request.

### Details

#### R1 - Dangling Symlink Component Bypass
- What happens: Path validation can miss dangling symlink components during traversal checks.
- Why it matters: A symlink that is unresolved at validation time can later resolve to an external location.
- Impact: Read and write operations may escape workspace boundaries.
- Affected area: src/security/path.rs (check_symlink_escape).

#### R2 - TOCTOU Between Validation and Use
- What happens: The path is validated first, then used later for filesystem operations.
- Why it matters: A concurrent filesystem change can swap path components after validation but before open/write.
- Impact: Race-based workspace escape is possible.
- Affected area: Filesystem and file-consuming tools that call validate_path_in_workspace before I/O.

#### R3 - Hardlink Alias Bypass
- What happens: A file inside workspace can be a hardlink to an inode outside the intended workspace trust boundary.
- Why it matters: Prefix and symlink checks can pass while data access still mutates or reads external content.
- Impact: Policy bypass for read/write operations.
- Affected area: Any tool that reads or writes via validated paths.

#### Risk Matrix

| ID | Risk | Severity | Likelihood | Impact |
|---|---|---|---|---|
| R1 | Dangling symlink component bypass | High | Medium | Workspace boundary escape for read/write |
| R2 | Validate/use TOCTOU race | High | Medium | Race-based boundary escape during file I/O |
| R3 | Hardlink alias bypass | Medium | Low-Medium | External inode read/write through in-workspace path |

### PoC

#### R1 - Dangling symlink component bypass
1. Create a symlink inside workspace pointing to a missing target.
2. Validate a path traversing that symlink.
3. Create the target directory outside workspace after validation.
4. Perform file operation and observe potential boundary escape if not fail-closed.

#### R2 - TOCTOU between validation and use
1. Validate a candidate in-workspace path.
2. Before open/write, replace an intermediate component with a link to external location.
3. Continue with the file operation.
4. Observe boundary escape if operation trusts only stale validation result.

#### R3 - Hardlink alias bypass
1. Place a hardlink inside workspace that points to an external inode.
2. Validate the in-workspace hardlink path.
3. Read or write through this path.
4. Observe external inode access through a path that appears in-scope.

### Impacts
Unauthorized cross path boundary

## Credit
[@zpbrent](https://github.com/zpbrent)

### Patch
[f50c17e11ae3e2d40c96730abac41974ef2ee2a8](https://github.com/qhkm/zeptoclaw/commit/f50c17e11ae3e2d40c96730abac41974ef2ee2a8)

## References
- https://github.com/qhkm/zeptoclaw/security/advisories/GHSA-2m67-cxxq-c3h8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32232
- https://github.com/qhkm/zeptoclaw/pull/324
- https://github.com/qhkm/zeptoclaw/commit/bf004a20d3687a0c1a9e052ec79536e30d6de134
- https://github.com/qhkm/zeptoclaw/commit/f50c17e11ae3e2d40c96730abac41974ef2ee2a8
- https://github.com/qhkm/zeptoclaw
- https://github.com/qhkm/zeptoclaw/releases/tag/v0.7.6
