# [H] BIT-node-2023-32559

## Summary
Severity: High
Advisory: BIT-node-2023-32559
Aliases: BIT-node-min-2023-32559, CVE-2023-32559
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-32559
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <20.5.1

## Details
A privilege escalation vulnerability exists in the experimental policy mechanism in all active release lines: 16.x, 18.x and, 20.x. The use of the deprecated API `process.binding()` can bypass the policy mechanism by requiring internal modules and eventually take advantage of `process.binding('spawn_sync')` run arbitrary code, outside of the limits defined in a `policy.json` file. Please note that at the time this CVE was issued, the policy is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/1946470
- https://security.netapp.com/advisory/ntap-20231006-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2023-32559
- https://lists.debian.org/debian-lts-announce/2024/09/msg00029.html
