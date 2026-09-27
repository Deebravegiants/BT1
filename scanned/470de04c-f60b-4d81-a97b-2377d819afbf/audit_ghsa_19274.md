# [M] Prevent GitHub CLI and extensions from executing arbitrary commands from compromised GitHub Enterprise Server

## Summary
Severity: Medium
Advisory: GHSA-g9f5-x53j-h563
CVE: CVE-2025-48938
CWE: CWE-501
Ecosystem: Go
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-g9f5-x53j-h563
Type: github-advisory

## Affected
- Go: `github.com/cli/go-gh/v2` — affected >=0 <2.12.1

## Details
### Summary

A security vulnerability has been identified in `go-gh` where an attacker-controlled GitHub Enterprise Server could result in executing arbitrary commands on a user's machine by replacing HTTP URLs provided by GitHub with local file paths for browsing. 

### Details

The GitHub CLI and CLI extensions allow users to transition from their terminal for a variety of use cases through the [`Browser` capability in `github.com/cli/go-gh/v2/pkg/browser`](https://github.com/cli/go-gh/blob/61bf393cf4aeea6d00a6251390f5f67f5b67e727/pkg/browser/browser.go):

- Using the `-w, --web` flag, GitHub CLI users can view GitHub repositories, issues, pull requests, and more using their web browser
- Using the `gh codespace` command set, GitHub CLI users can transition to Visual Studio Code to work with GitHub Codespaces

This is done by using URLs provided through API responses from authenticated GitHub hosts when users execute `gh` commands.

Prior to `2.12.1`, `Browser.Browse()` would attempt to open the provided URL using a variety of OS-specific approaches regardless of the scheme.  An attacker-controlled GitHub Enterprise Server could modify API responses to use a specially tailored local executable path instead of HTTP URLs to resources.  This could allow the attacker to execute arbitrary executables on the user's machine. 

In `2.12.1`, `Browser.Browse()` has been enhanced to allow and disallow a variety of scenarios to avoid opening or executing files on the filesystem without unduly impacting HTTP URLs:

1. URLs with `http://`, `https://`, `vscode://`, `vscode-insiders://` protocols are supported
1. URLs with `file://` protocol are unsupported
1. URLs matching files or directories on the filesystem are unsupported
1. URLs matching executables in the user's path are unsupported

URLs without protocols will be browsable if none of these other conditions apply.

As we have more information about use cases, maintainers can expand these capabilities for an improved user experience that allows configuring allowed URL schemes and/or prompt the user for an unexpected user case and confirming whether to continue.

### Impact

Successful exploitation could cause users of the attacker-controlled GitHub Enterprise Server to execute arbitrary commands.

### Remediation and Mitigation

1. Upgrade `go-gh` to `2.12.1`

## References
- https://github.com/cli/go-gh/security/advisories/GHSA-g9f5-x53j-h563
- https://nvd.nist.gov/vuln/detail/CVE-2025-48938
- https://github.com/cli/go-gh/commit/a08820a13f257d6c5b4cb86d37db559ec6d14577
- https://github.com/cli/go-gh
