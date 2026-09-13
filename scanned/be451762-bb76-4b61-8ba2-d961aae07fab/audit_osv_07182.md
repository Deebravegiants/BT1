# [H] BIT-node-2026-48618

## Summary
Severity: High
Advisory: BIT-node-2026-48618
Aliases: BIT-node-min-2026-48618, CVE-2026-48618
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-node-2026-48618
Type: osv

## Affected
- Bitnami: `node` — affected >=26.3.0 <26.3.1

## Details
A flaw in Node.js TLS hostname handling can cause Node.js unicode dot separator handling can lead to tls wildcard-depth authentication bypass due to resolver and verifier hostname normalization mismat.

This can lead to confidentiality impact or bypass of the intended security boundary under affected configurations.

This vulnerability affects all supported release lines: **Node.js 22**, **Node.js 24**, and **Node.js 26**.

## References
- https://nodejs.org/en/blog/vulnerability/june-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-48618
- https://access.redhat.com/errata/RHSA-2026:28727
- https://access.redhat.com/errata/RHSA-2026:29012
- https://access.redhat.com/errata/RHSA-2026:30172
- https://access.redhat.com/errata/RHSA-2026:35841
- https://access.redhat.com/errata/RHSA-2026:35842
- https://access.redhat.com/errata/RHSA-2026:35891
- https://access.redhat.com/errata/RHSA-2026:35892
- https://access.redhat.com/errata/RHSA-2026:39246
- https://access.redhat.com/errata/RHSA-2026:7378
- https://access.redhat.com/errata/RHSA-2026:9455
- https://access.redhat.com/security/cve/CVE-2026-48618
- https://bugzilla.redhat.com/show_bug.cgi?id=2493337
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48618.json
- https://access.redhat.com/errata/RHSA-2026:39868
- https://access.redhat.com/errata/RHSA-2026:41947
- https://access.redhat.com/errata/RHSA-2026:52399
