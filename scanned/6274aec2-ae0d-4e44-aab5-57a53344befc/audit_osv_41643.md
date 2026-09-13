# [M] Fedify: Server-Side Request Forgery in getNodeInfo() Allows Access to Internal Network Resources

## Summary
Severity: Medium
Advisory: CVE-2026-62857
Aliases: GHSA-hqph-j65v-8cq5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-62857
Type: osv

## Details
Fedify is a TypeScript library for building federated server apps powered by ActivityPub. From version 1.2.0 through the affected 1.9, 1.10, 2.0, 2.1, 2.2, and 2.3 maintenance lines, getNodeInfo() follows an attacker-controlled links[].href value from /.well-known/nodeinfo without scheme, redirect, or private-address validation, allowing requests to loopback, link-local, cloud metadata, and private-network services and returning their response bodies. This issue is fixed in versions 1.9.13, 1.10.12, 2.0.22, 2.1.18, 2.2.7, and 2.3.2.

## References
- https://github.com/fedify-dev/fedify/releases/tag/2.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62857.json
- https://github.com/fedify-dev/fedify/security/advisories/GHSA-hqph-j65v-8cq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-62857
