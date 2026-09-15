# [C] Ceph Monitor subscription handler improperly authorizes config-key store reads, exposing cluster secrets to read-only users

## Summary
Severity: Critical
Advisory: BIT-ceph-2026-50152
Aliases: CVE-2026-50152, GHSA-rg9p-5xcp-wm8h
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-ceph-2026-50152
Type: osv

## Affected
- Bitnami: `ceph` — affected >=20.0.0 <20.2.4

## Details
Ceph is an open-source distributed storage platform providing object, block, and file storage. In versions prior to 20.2.4 and 19.2.6, the Monitor subscription handler fails to properly authorize access to the configuration-key store, allowing any CephX user with only  `mon allow r` capabilities to read the entire store by sending a single crafted MMonSubscribe message. The config-key store holds sensitive secrets including OSD LUKS disk-encryption passphrases and, on cephadm-managed clusters, the SSH private key that cephadm uses to reach every host in the cluster. Because that key grants root on every node under the default cephadm configuration, a low-privileged read-only account can escalate to full cluster and host compromise. This issue is fixed in versions 20.2.4 and 19.2.6

## References
- https://github.com/ceph/ceph/commit/d971bb2b6199f70b1708a20a63fa944ee7a94727
- https://github.com/ceph/ceph/commit/f2840d2fd338ab5de2865f0f78684bbf7b888c84
- https://github.com/ceph/ceph/security/advisories/GHSA-rg9p-5xcp-wm8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-50152
