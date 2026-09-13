# [H] Ceph: AES-CBC misuse in CephX and RADOSGW enables authentication bypass and credential forgery

## Summary
Severity: High
Advisory: BIT-ceph-2025-30156
Aliases: CVE-2025-30156, GHSA-7q3q-3975-qw3q
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-ceph-2025-30156
Type: osv

## Affected
- Bitnami: `ceph` — affected >=20.0.0 <20.2.4

## Details
Ceph is an open-source distributed storage platform providing object, block, and file storage. In versions prior to 20.2.4 and 19.2.6, the CephX authentication protocol encrypts tickets with AES-128-CBC in an unauthenticated mode that uses a hard-coded initialization vector and no message authentication, allowing an attacker to forge credentials and gain cluster-wide access. Because the ciphertext is malleable and the monitor will encrypt attacker-chosen entity names, an attacker holding one low-privilege key and able to observe CephX traffic can use the monitor as an encryption oracle and splice ciphertext blocks into valid tickets for privileged entities such as Manager, MDS, and OSD. The same lack of authentication also lets an attacker with CephX permissions escalate privileges by flipping a single bit in a service ticket to set its allow_all field to true. This issue is fixed in versions 20.2.4 and 19.2.6.

## References
- https://github.com/ceph/ceph/commit/2ba086255de09c8b95177717cc7e9dd4377e2f0f
- https://github.com/ceph/ceph/commit/3078188a7bdd89e2975280f2a906c71c2f6effd6
- https://github.com/ceph/ceph/security/advisories/GHSA-7q3q-3975-qw3q
- https://nvd.nist.gov/vuln/detail/CVE-2025-30156
