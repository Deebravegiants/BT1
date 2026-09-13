# [H] Portainer Portainer CE - Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-72533
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72533
Type: osv

## Details
An authentication bypass vulnerability in Portainer CE through 2.44.0 allows authenticated low-privileged users to bypass Docker proxy authorization checks via non-canonical URL normalization, defeating all authorization middleware. The proxy endpoint fails to normalize request paths before applying access controls, allowing crafted requests to be interpreted differently by the proxy and the authorization layer. Successful exploitation grants the attacker root-level access to the underlying Docker host.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72533
- https://github.com/portainer/portainer
