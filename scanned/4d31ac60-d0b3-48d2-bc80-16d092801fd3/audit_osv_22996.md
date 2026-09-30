# [H] Git clone remote code execution vulnerability in git-for-windows

## Summary
Severity: High
Advisory: CVE-2022-41953
Aliases: GHSA-v4px-mx59-w99c
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-41953
Type: osv

## Details
Git GUI is a convenient graphical tool that comes with Git for Windows. Its target audience is users who are uncomfortable with using Git on the command-line. Git GUI has a function to clone repositories. Immediately after the local clone is available, Git GUI will automatically post-process it, among other things running a spell checker called `aspell.exe` if it was found. Git GUI is implemented as a Tcl/Tk script. Due to the unfortunate design of Tcl on Windows, the search path when looking for an executable _always includes the current directory_. Therefore, malicious repositories can ship with an `aspell.exe` in their top-level directory which is executed by Git GUI without giving the user a chance to inspect it first, i.e. running untrusted code. This issue has been addressed in version 2.39.1. Users are advised to upgrade. Users unable to upgrade should avoid using Git GUI for cloning. If that is not a viable option, at least avoid cloning from untrusted sources.

## References
- https://www.tcl.tk/man/tcl8.6/TclCmd/exec.html#M23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41953.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-v4px-mx59-w99c
- https://nvd.nist.gov/vuln/detail/CVE-2022-41953
- https://github.com/git-for-windows/git/commit/7360767e8dfc1895a932324079f7d45d7791d39f
- https://github.com/git-for-windows/git/pull/4219
