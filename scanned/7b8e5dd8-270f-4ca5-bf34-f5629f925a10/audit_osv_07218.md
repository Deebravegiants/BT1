# [H] OpenBao's Namespace Deletion May Not Delete Data Properly

## Summary
Severity: High
Advisory: BIT-openbao-2026-42186
Aliases: CVE-2026-42186, GHSA-vv66-6rp4-wr4f, GO-2026-5674
Ecosystem: Bitnami
Published: 2026-07-27
Source: https://osv.dev/vulnerability/BIT-openbao-2026-42186
Type: osv

## Affected
- Bitnami: `openbao` — affected >=0 <2.5.3

## Details
OpenBao is an open source identity-based secrets management system. Prior to 2.5.3, when OpenBao's initial namespace deletion fails, subsequent retries fail to properly remove all data before marking the namespace as deleted. This can affect any outstanding leases as well as potentially leaving unrelated storage entries around. This vulnerability is fixed in 2.5.3.

## References
- https://github.com/openbao/openbao/commit/6d2e0506e2b41be0eaa6643bf7b4efc9a2c09445
- https://github.com/openbao/openbao/releases/tag/v2.5.3
- https://github.com/openbao/openbao/security/advisories/GHSA-vv66-6rp4-wr4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-42186
