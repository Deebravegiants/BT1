# [H] Consul vulnerable to an authorization bypass in the catalog node-write path

## Summary
Severity: High
Advisory: CVE-2026-87090
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-87090
Type: osv

## Details
Consul and Consul Enterprise are vulnerable to an authorization bypass in the catalog node-write path that may allow an authenticated attacker to delete another node's catalog registration and take over its node identity. An attacker with a token granting node-write permission on any single node name may exploit this issue if they can obtain the node ID of a node they do not control. This vulnerability (CVE-2026-87090) is fixed in Consul 2.0.4 and Consul Enterprise 1.21.18, 1.22.12 and 2.0.4.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-34-consul-vulnerable-to-an-authorization-bypass-in-the-catalog-node-write-path/77736
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87090.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-87090
- https://github.com/hashicorp/consul
