# [H] Ceph: CephX AES Authentication error

## Summary
Severity: High
Advisory: BIT-ceph-2026-39944
Aliases: CVE-2026-39944, GHSA-j73r-qrgx-jvq2
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-ceph-2026-39944
Type: osv

## Affected
- Bitnami: `ceph` — affected >=20.0.0 <20.2.4

## Details
Ceph is an open-source distributed storage platform providing object, block, and file storage. In versions prior to 20.2.4 and 19.2.6, the RADOS Gateway (RGW) protects STS session tokens with an AES-128-CBC handler that provides no message authentication, allowing an attacker who holds any valid STS token to tamper with it undetected and escalate to full RGW administrative access. Because the ciphertext is unauthenticated, the attacker can perform a CBC bit-flip on the acct_type, perm_type, and is_admin fields of their own token, and a forged is_admin value triggers a global administrative override that bypasses all capability checks. The attack is reachable remotely over the RGW S3 endpoint and is a self-contained modification of a token the attacker already possesses, requiring no encryption oracle and no network observation. It requires only a single valid STS token, which need not carry any elevated privileges, with STS enabled. This issue is fixed in versions 20.2.4 and 19.2.6.

## References
- https://github.com/ceph/ceph/releases/tag/v19.2.6
- https://github.com/ceph/ceph/releases/tag/v20.2.4
- https://github.com/ceph/ceph/security/advisories/GHSA-j73r-qrgx-jvq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39944
