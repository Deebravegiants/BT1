# [H] Netmaker Vulnerable to Privilege Escalation From Non Admin To Admin User

## Summary
Severity: High
Advisory: GHSA-826j-8wp2-4x6q
CVE: CVE-2023-32079
CWE: CWE-915
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-826j-8wp2-4x6q
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <0.17.1
- Go: `github.com/gravitl/netmaker` — affected >=0.18.0 <0.18.6

## Details
### Impact
A Mass assignment vulnerability was found allowing a non-admin user to escalate privileges to admin user.

### Patches
Issue is patched in 0.17.1, and fixed in 0.18.6+.

If Users are using 0.17.1, they should run "docker pull gravitl/netmaker:v0.17.1" and "docker-compose up -d". This will switch them to the patched users

If users are using v0.18.0-0.18.5, they should upgrade to v0.18.6 or later.

### Workarounds
If using 0.17.1, can just pull the latest docker image of backend and restart server.

### References
Credit to Project Discovery, and in particular https://github.com/rootxharsh , https://github.com/iamnoooob, and https://github.com/projectdiscovery

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-826j-8wp2-4x6q
- https://nvd.nist.gov/vuln/detail/CVE-2023-32079
- https://github.com/gravitl/netmaker
