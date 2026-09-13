# [H] BIT-ceph-2020-1699

## Summary
Severity: High
Advisory: BIT-ceph-2020-1699
Aliases: CVE-2020-1699
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2020-1699
Type: osv

## Affected
- Bitnami: `ceph` — affected >=15.0.0

## Details
A path traversal flaw was found in the Ceph dashboard implemented in upstream versions v14.2.5, v14.2.6, v15.0.0 of Ceph storage and has been fixed in versions 14.2.7 and 15.1.0. An unauthenticated attacker could use this flaw to cause information disclosure on the host machine running the Ceph dashboard.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1699
- https://nvd.nist.gov/vuln/detail/CVE-2020-1699
