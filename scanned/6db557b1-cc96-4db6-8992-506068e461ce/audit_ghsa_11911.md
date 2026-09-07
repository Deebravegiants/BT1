# [H] Local Incus UI web server vulnerable to nuthentication bypass

## Summary
Severity: High
Advisory: GHSA-453r-g2pg-cxxq
CVE: CVE-2026-33898
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-453r-g2pg-cxxq
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incus` — affected >=0 <6.23.0

## Details
### Summary
The web server spawned by `incus webui` incorrectly validates the authentication token such that an invalid value will be accepted.

### Details
`incus webui` runs a local web server on a random localhost port. For authentication, it provides the user with a URL containing an authentication token. When accessed with that token, Incus creates a cookie persisting that token without needing to include it in subsequent HTTP requests.

While the Incus client correctly validates the value of the cookie, it does not correctly validate the token when passed int the URL.
This allows for an attacker able to locate and talk to the temporary web server on localhost to have as much access to Incus as the user who ran `incus webui`.

This can lead to privilege escalation by another local user or an access to the user's Incus instances and possibly system resources by a remote attack able to trick the local user into interacting with the Incus UI web server.

### Credit
This issue was discovered and reported by the team at [7asecurity](https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-453r-g2pg-cxxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33898
- https://github.com/lxc/incus/commit/d81d49e746e15dad35de39dc0ace0cedfba7d2f7
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v6.23.0
