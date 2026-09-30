# [C] Arbitrary code execution due to an uncontrolled search path for the git binary

## Summary
Severity: Critical
Advisory: GHSA-m898-h4pm-pqfr
CVE: CVE-2021-28955
CWE: CWE-427
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-25
Source: https://github.com/advisories/GHSA-m898-h4pm-pqfr
Type: github-advisory

## Affected
- Go: `github.com/MichaelMure/git-bug` — affected >=0 <0.7.2

## Details
### Impact

The go language recently addressed a security issue in the way that binaries are found before being executed. Some operating systems like Windows persist to have the current directory being part of the default search path, and having priority over the system-wide path.

This means that it's possible for a malicious user to craft for example a `git.bat` command, commit it and push it in a repository. Later when git-bug search for the git binary, this malicious executable can take priority  and be executed.

### Who is impacted

This issue happen on Windows and some other operating systems with a badly configured PATH.

All version prior to 0.7.2 are vulnerable to this issue.

### Patches

Version 0.7.2 fix this issue. Users should update as soon as possible.

### References

More details about this issue can be found [here](https://blog.golang.org/path-security).

## References
- https://github.com/git-bug/git-bug/security/advisories/GHSA-m898-h4pm-pqfr
- https://nvd.nist.gov/vuln/detail/CVE-2021-28955
- https://github.com/MichaelMure/git-bug/pull/604
- https://github.com/git-bug/git-bug
- https://vuln.ryotak.me/advisories/18
