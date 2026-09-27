# [H] Ceph RGW SigV4 handler accepts unsigned x-amz-* headers on presigned requests, allowing privilege escalation

## Summary
Severity: High
Advisory: BIT-ceph-2026-54330
Aliases: CVE-2026-54330, GHSA-rmjq-ffrm-j6vj
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-ceph-2026-54330
Type: osv

## Affected
- Bitnami: `ceph` — affected >=20.0.0 <20.2.4

## Details
Ceph is an open-source distributed storage platform providing object, block, and file storage. In versions prior to 20.2.4 and 19.2.6, the Ceph Object Gateway (RGW) SigV4 handler does not reject requests that carry x-amz-* headers absent from the signed header set, allowing anyone holding a presigned URL to attach arbitrary unsigned x-amz-* headers that RGW will honor. AWS S3 requires every x-amz-* header on a SigV4 request to be signed and rejects requests bearing additional unsigned headers, but RGW validates only the headers listed in X-Amz-SignedHeaders and ignores any extra ones, so they take effect without being covered by the signature. By adding such headers to a presigned PUT URL, an attacker can grant themselves more capabilities than the URL's signer intended and escalate their privileges. This issue is fixed in versions 20.2.4 and 19.2.6.

## References
- https://github.com/ceph/ceph/commit/5837aa8e60471128dbb672b0ff6f1b1feebe08a7
- https://github.com/ceph/ceph/commit/5978c866d4a0812fbb024745c4f1e79aaecd6c6a
- https://github.com/ceph/ceph/security/advisories/GHSA-rmjq-ffrm-j6vj
- https://nvd.nist.gov/vuln/detail/CVE-2026-54330
