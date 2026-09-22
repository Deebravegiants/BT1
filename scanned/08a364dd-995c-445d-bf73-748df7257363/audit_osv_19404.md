# [H] CVE-2021-21237

## Summary
Severity: High
Advisory: CVE-2021-21237
Aliases: BIT-git-lfs-2021-21237, GHSA-cx3w-xqmc-84g5, GO-2021-0098
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21237
Type: osv

## Details
Git LFS is a command line extension for managing large files with Git. On Windows, if Git LFS operates on a malicious repository with a git.bat or git.exe file in the current directory, that program would be executed, permitting the attacker to execute arbitrary code. This does not affect Unix systems. This is the result of an incomplete fix for CVE-2020-27955. This issue occurs because on Windows, Go includes (and prefers) the current directory when the name of a command run does not contain a directory separator. Other than avoiding untrusted repositories or using a different operating system, there is no workaround. This is fixed in v2.13.2.

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-27955
- https://github.com/git-lfs/git-lfs/releases/tag/v2.13.2
- https://github.com/git-lfs/git-lfs/security/advisories/GHSA-cx3w-xqmc-84g5
- https://github.com/git-lfs/git-lfs/commit/fc664697ed2c2081ee9633010de0a7f9debea72a
