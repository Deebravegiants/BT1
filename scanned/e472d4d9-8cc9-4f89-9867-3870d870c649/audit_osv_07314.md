# [M] BIT-postgresql-2021-3677

## Summary
Severity: Medium
Advisory: BIT-postgresql-2021-3677
Aliases: CVE-2021-3677
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-3677
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=13.0.0 <13.4.0

## Details
A flaw was found in postgresql. A purpose-crafted query can read arbitrary bytes of server memory. In the default configuration, any authenticated database user can complete this attack at will. The attack does not require the ability to create objects. If server settings include max_worker_processes=0, the known versions of this attack are infeasible. However, undiscovered variants of the attack may be independent of that setting.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2001857
- https://security.gentoo.org/glsa/202211-04
- https://security.netapp.com/advisory/ntap-20220407-0008/
- https://www.postgresql.org/support/security/CVE-2021-3677/
- https://nvd.nist.gov/vuln/detail/CVE-2021-3677
