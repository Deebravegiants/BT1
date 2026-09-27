# [H] Malformed Valkey Cluster bus message can lead to Remote DoS

## Summary
Severity: High
Advisory: BIT-valkey-2026-21863
Aliases: CVE-2026-21863, GHSA-c677-q3wr-gggq
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-valkey-2026-21863
Type: osv

## Affected
- Bitnami: `valkey` — affected >=9.0.0 <9.0.2

## Details
Valkey is a distributed key-value database. Prior to versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12, a malicious actor with access to the Valkey clusterbus port can send an invalid packet that may cause an out bound read, which might result in the system crashing. The Valkey clusterbus packet processing code does not validate that a clusterbus ping extension packet is located within buffer of the clusterbus packet before attempting to read it. Versions 9.0.2, 8.1.6, 8.0.7, and 7.2.12 fix the issue. As an additional mitigation, don't expose the cluster bus connection directly to end users, and protect the connection with its own network ACLs.

## References
- https://github.com/valkey-io/valkey/security/advisories/GHSA-c677-q3wr-gggq
- https://nvd.nist.gov/vuln/detail/CVE-2026-21863
- https://access.redhat.com/errata/RHSA-2026:3443
- https://access.redhat.com/errata/RHSA-2026:3507
- https://access.redhat.com/errata/RHSA-2026:5445
- https://access.redhat.com/errata/RHSA-2026:8753
- https://access.redhat.com/security/cve/CVE-2026-21863
- https://bugzilla.redhat.com/show_bug.cgi?id=2442026
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21863.json
