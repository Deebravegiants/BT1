# [H] Netmaker has Hardcoded DNS Secret Key

## Summary
Severity: High
Advisory: GHSA-8x8h-hcq8-jwwx
CVE: CVE-2023-32077
CWE: CWE-321, CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-8x8h-hcq8-jwwx
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <0.17.1
- Go: `github.com/gravitl/netmaker` — affected >=0.18.0 <0.18.6

## Details
### Impact 
Hardcoded DNS key usage has been found in Netmaker allowing unauth users to interact with DNS API endpoints.

### Patches
Issue is patched in 0.17.1, and fixed in 0.18.6+. 

If Users are using 0.17.1, they should run "docker pull gravitl/netmaker:v0.17.1" and "docker-compose up -d". This will switch them to the patched users

If users are using v0.18.0-0.18.5, they should upgrade to v0.18.6 or later.

### Workarounds
If using 0.17.1, can just pull the latest docker image of backend and restart server.

### References
Credit to Project Discovery, and in particular https://github.com/rootxharsh , https://github.com/iamnoooob, and https://github.com/projectdiscovery

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-8x8h-hcq8-jwwx
- https://nvd.nist.gov/vuln/detail/CVE-2023-32077
- https://github.com/gravitl/netmaker/pull/2170
- https://github.com/gravitl/netmaker/commit/1621c27c1d176b639e9768b2acad7693e387fd51
- https://github.com/gravitl/netmaker/commit/9362c39a9a822f0e07361aa7c77af2610597e657
- https://github.com/gravitl/netmaker
