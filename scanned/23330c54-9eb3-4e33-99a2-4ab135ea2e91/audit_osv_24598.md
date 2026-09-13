# [H] gitk can inadvertently call executables in the worktree

## Summary
Severity: High
Advisory: CVE-2023-23618
Aliases: GHSA-wxwv-49qw-35pm
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-23618
Type: osv

## Details
Git for Windows is the Windows port of the revision control system Git. Prior to Git for Windows version 2.39.2, when `gitk` is run on Windows, it potentially runs executables from the current directory inadvertently, which can be exploited with some social engineering to trick users into running untrusted code. A patch is available in version 2.39.2. As a workaround, avoid using `gitk` (or Git GUI's "Visualize History" functionality) in clones of untrusted repositories.

## References
- https://github.com/git-for-windows/git/releases/tag/v2.39.2.windows.1
- https://wiki.tcl-lang.org/page/exec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23618.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-wxwv-49qw-35pm
- https://nvd.nist.gov/vuln/detail/CVE-2023-23618
- https://github.com/git-for-windows/git/commit/49a8ec9dac3cec6602f05fed1b3f80a549c8c05c
