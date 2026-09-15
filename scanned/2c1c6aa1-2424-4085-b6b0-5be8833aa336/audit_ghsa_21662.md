# [C] Git LFS can execute a Git binary from the current directory

## Summary
Severity: Critical
Advisory: GHSA-4g4p-42wc-9f3m
CVE: CVE-2020-27955
CWE: CWE-427
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-4g4p-42wc-9f3m
Type: github-advisory

## Affected
- Go: `github.com/git-lfs/git-lfs` — affected >=0 <2.12.1

## Details
### Impact
On Windows, if Git LFS operates on a malicious repository with a `git.bat` or `git.exe` file in the current directory, that program would be executed, permitting the attacker to execute arbitrary code.  This does not affect Unix systems.

This occurs because on Windows, Go includes (and prefers) the current directory when the name of a command run does not contain a directory separator.

### Patches
This version should be patched in v2.12.1, which will be released in coordination with this security advisory.

### Workarounds
Other than avoiding untrusted repositories, there is no workaround.

### For more information
If you have any questions or comments about this advisory:
* Start a discussion in [the Git LFS discussion page](https://github.com/git-lfs/git-lfs/discussions).
* If you cannot open a discussion, please email the core team using their usernames at `github.com`.

## References
- https://github.com/git-lfs/git-lfs/security/advisories/GHSA-4g4p-42wc-9f3m
- https://nvd.nist.gov/vuln/detail/CVE-2020-27955
- https://github.com/git-lfs/git-lfs
- https://github.com/git-lfs/git-lfs/releases
- https://legalhackers.com/advisories/Git-LFS-RCE-Exploit-CVE-2020-27955.html
- http://seclists.org/fulldisclosure/2020/Nov/1
