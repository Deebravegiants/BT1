# [M] go-git: Credential leak via cross-host redirect in smart HTTP transport

## Summary
Severity: Medium
Advisory: GHSA-3xc5-wrhm-f963
CVE: CVE-2026-41506
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-3xc5-wrhm-f963
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.18.0
- Go: `github.com/go-git/go-git/v6` — affected >=0 <6.0.0-alpha.2

## Details
### Impact
`go-git` may leak HTTP authentication credentials when following redirects during smart-HTTP clone and fetch operations.

If a remote repository responds to the initial `/info/refs` request with a redirect to a different host, go-git updates the session endpoint to the redirected location and reuses the original authentication for subsequent requests. This can result in the credentials (e.g. Authorization headers) being sent to an unintended host.

An attacker controlling or influencing the redirect target can capture these credentials and potentially reuse them to access the victim’s repositories or other resources, depending on the scope of the credential.

**Clients using `go-git` exclusively with trusted remotes (for example, GitHub or GitLab), and over a secure HTTPS connection, are not affected by this issue.** The risk arises when interacting with untrusted or misconfigured Git servers, or when using unsecured HTTP connections, which is not recommended. Such configurations also expose clients to a broader class of security risks beyond this issue, including credential interception and tampering of repository data.

### Patches
Users should upgrade to `v5.18.0`, or `v6.0.0-alpha.2`, in order to mitigate this vulnerability. Versions prior to v5 are likely to be affected, users are recommended to upgrade to a supported `go-git` version.

The patched versions add support for configuring [followRedirects](https://git-scm.com/docs/git-config#Documentation/git-config.txt-httpfollowRedirects). In line with upstream behaviour, the default is now `initial`, while users can opt into `FollowRedirects` or `NoFollowRedirects` programmatically.

### Credit
Thanks to the 3 separate reports from @celinke97, @N0zoM1z0 and @AyushParkara. Thanks for finding and reporting this issue privately to the `go-git` project. :bow:

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-3xc5-wrhm-f963
- https://nvd.nist.gov/vuln/detail/CVE-2026-41506
- https://github.com/go-git/go-git
- https://github.com/go-git/go-git/releases/tag/v5.18.0
- https://github.com/go-git/go-git/releases/tag/v6.0.0-alpha.2
