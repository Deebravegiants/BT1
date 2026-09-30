# [H] Secret insertion into debug log in Docker

## Summary
Severity: High
Advisory: GHSA-j249-ghv5-7mxv
CVE: CVE-2019-13509
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j249-ghv5-7mxv
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <18.09.8

## Details
In Docker CE and EE before 18.09.8 (as well as Docker EE before 17.06.2-ee-23 and 18.x before 18.03.1-ee-10), Docker Engine in debug mode may sometimes add secrets to the debug log. This applies to a scenario where docker stack deploy is run to redeploy a stack that includes (non external) secrets. It potentially applies to other API users of the stack API if they resend the secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13509
- https://docs.docker.com/engine/release-notes/18.09
