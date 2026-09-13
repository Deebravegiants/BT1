# [H] Netmaker IDOR Allows User to Update Other User's Password

## Summary
Severity: High
Advisory: GHSA-256m-j5qw-38f4
CVE: CVE-2023-32078
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-256m-j5qw-38f4
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <0.17.1
- Go: `github.com/gravitl/netmaker` — affected >=0.18.0 <0.18.6

## Details
### Impact
An IDOR vulnerability was found in the user update function. By specifying another user's username it is possible to update the other user's password.

### Patches
Issue is patched in 0.17.1, and fixed in 0.18.6+.

If Users are using 0.17.1, they should run "docker pull gravitl/netmaker:v0.17.1" and "docker-compose up -d". This will switch them to the patched users

If users are using v0.18.0-0.18.5, they should upgrade to v0.18.6 or later.

### Workarounds
If using 0.17.1, can just pull the latest docker image of backend and restart server.

### References
Credit to Project Discovery, and in particular https://github.com/rootxharsh , https://github.com/iamnoooob, and https://github.com/projectdiscovery

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-256m-j5qw-38f4
- https://nvd.nist.gov/vuln/detail/CVE-2023-32078
- https://github.com/gravitl/netmaker/pull/2158
- https://github.com/gravitl/netmaker/commit/b3be57c65bf0bbfab43b66853c8e3637a43e2839
- https://github.com/gravitl/netmaker
