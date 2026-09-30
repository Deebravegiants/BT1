# [H] Ceph is vulnerable to authentication bypass through RadosGW

## Summary
Severity: High
Advisory: BIT-ceph-2024-48916
Aliases: CVE-2024-48916, GHSA-5g9m-mmp6-93mq
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2024-48916
Type: osv

## Affected
- Bitnami: `ceph` — affected >=0 <20.2.1

## Details
Ceph is a distributed object, block, and file storage platform. In versions 19.2.3 and below, it is possible to send an JWT that has "none" as JWT alg. And by doing so the JWT signature is not checked. The vulnerability is most likely in the RadosGW OIDC provider. As of time of publication, a known patched version has yet to be published.

## References
- https://github.com/ceph/ceph/security/advisories/GHSA-5g9m-mmp6-93mq
- https://nvd.nist.gov/vuln/detail/CVE-2024-48916
