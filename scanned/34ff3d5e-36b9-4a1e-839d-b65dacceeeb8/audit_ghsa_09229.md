# [H] Dulwich has an arbitrary file write via NTFS-hostile tree entries on Windows

## Summary
Severity: High
Advisory: GHSA-897w-fcg9-f6xj
CVE: CVE-2026-42305
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-897w-fcg9-f6xj
Type: github-advisory

## Affected
- PyPI: `dulwich` — affected >=0.10.0 <1.2.5

## Details
## Impact

Arbitrary file write leading to remote code execution when cloning or checking out a malicious Git repository on Windows.

Dulwich's path-element validator accepted tree entries whose filenames contained bytes that Windows interprets as structural path syntax:

  - \ — the Windows path separator. A single tree entry named .git\hooks\pre-commit.exe was treated as one valid filename on POSIX but materialized as nested directories .git/hooks/pre-commit.exe on Windows, planting a file inside the victim's .git directory. Git for Windows then
  executes that hook on the next git commit, giving the attacker arbitrary code execution in the victim's user context. The same primitive can be used with ..\outside.txt to escape the work tree.
  - : — the NTFS alternate-data-stream marker. .git::$INDEX_ALLOCATION writes directly into the victim's .git entity, bypassing the .git-as-a-directory check.
  - git~<digits> — NTFS 8.3 short-name aliases of .git. Only the literal git~1 was rejected; git~2, git~10, GIT~1, etc. were all accepted.

Contributing configuration bugs made matters worse. The core.protectNTFS and core.protectHFS settings were looked up under a wrong option name and so user-set values were silently ignored, and core.protectNTFS only defaulted to true on Windows (Git upstream has defaulted it to true everywhere since CVE-2019-1353). Both have been corrected.

Anyone who clones, fetches, or checks out an untrusted repository with Dulwich on Windows - either through the Dulwich CLI, porcelain.clone, or any downstream tool built on Dulwich - is impacted. POSIX clones are not directly exploitable (on POSIX \ is a literal filename byte), but a POSIX user can unknowingly propagate a malicious tree to Windows consumers via push or re-publication.

## Patches

Fixed in Dulwich 1.2.5. Users should upgrade to 1.2.5 or later.

The fix lives in three commits:

- Read core.protectNTFS / core.protectHFS under their documented option names so user-set values are honored.
- Default core.protectNTFS to true on every platform, matching Git's PROTECT_NTFS_DEFAULT=1.
- Reject \, :, and all git~<digits> 8.3 short-name forms in validate_path_element_ntfs.

## Workarounds

There is no effective pre-patch workaround. On affected versions the core.protectNTFS configuration key was silently ignored, so setting it to true does not mitigate the issue. Users who cannot upgrade should avoid cloning, fetching, or checking out untrusted repositories with Dulwich on Windows. After upgrading the NTFS validator is on by default on every platform, so no additional configuration is required.

## Resources

- Git upstream path validation: https://github.com/git/git/blob/master/path.c (is_ntfs_dotgit, verify_path)
- CVE-2019-1353 — the Git upstream vulnerability that established core.protectNTFS = true as the cross-platform default
- CVE-2019-1354 — backslash-in-tree-path class in Git, analogous to this issue

## References
- https://github.com/jelmer/dulwich/security/advisories/GHSA-897w-fcg9-f6xj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42305
- https://github.com/jelmer/dulwich/commit/49eb56e51aad637fc23d54bf2a08cb42739b8290
- https://github.com/jelmer/dulwich/commit/57efc4aa1581e038915a0fd79365be53b150f4a9
- https://github.com/jelmer/dulwich
- https://github.com/jelmer/dulwich/releases/tag/dulwich-1.2.5
