# [H] BIT-ceph-2020-10736

## Summary
Severity: High
Advisory: BIT-ceph-2020-10736
Aliases: CVE-2020-10736
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2020-10736
Type: osv

## Affected
- Bitnami: `ceph` — affected >=15.2.0 <15.2.2

## Details
An authorization bypass vulnerability was found in Ceph versions 15.2.0 before 15.2.2, where the ceph-mon and ceph-mgr daemons do not properly restrict access, resulting in gaining access to unauthorized resources. This flaw allows an authenticated client to modify the configuration and possibly conduct further attacks.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10736
- https://ceph.io/releases/v15-2-2-octopus-released/
- https://nvd.nist.gov/vuln/detail/CVE-2020-10736
