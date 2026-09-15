# [C] Command Injection Vulnerability with Mercurial in VCS

## Summary
Severity: Critical
Advisory: GHSA-6635-c626-vj4r
CVE: CVE-2022-21235
CWE: CWE-77, CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-6635-c626-vj4r
Type: github-advisory

## Affected
- Go: `github.com/Masterminds/vcs` — affected >=0 <1.13.2

## Details
URLs and local file paths passed to the Mercurial (hg) APIs that are specially crafted can contain commands which are executed by Mercurial if it is installed on the host operating system. The `vcs` package uses the underly version control system, in this case `hg`, to implement the needed functionality. When `hg` is executed, argument strings are passed to `hg` in a way that additional flags can be set. The additional flags can be used to perform a command injection. Other version control systems with an implemented interface may also be vulnerable. The issue has been fixed in version 1.13.2. A work around is to sanitize data passed to the `vcs` package APIs to ensure it does not contain commands or unexpected data. This is important for user input data that is passed directly to the package APIs.

## References
- https://github.com/Masterminds/vcs/security/advisories/GHSA-6635-c626-vj4r
- https://nvd.nist.gov/vuln/detail/CVE-2022-21235
- https://github.com/Masterminds/vcs/pull/105
- https://github.com/Masterminds/vcs/commit/922a5122330ea8fbe56352a0172ddb6bf019cd22
- https://github.com/Masterminds/vcs
- https://github.com/Masterminds/vcs/releases/tag/v1.13.2
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMMASTERMINDSVCS-2437078
