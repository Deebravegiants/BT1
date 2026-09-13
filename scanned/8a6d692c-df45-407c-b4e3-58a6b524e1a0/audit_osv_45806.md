# [M] JLSEC-2026-35

## Summary
Severity: Medium
Advisory: JLSEC-2026-35
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-35
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
A flaw was found in postgresql. A purpose-crafted query can read arbitrary bytes of server memory. In the default configuration, any authenticated database user can complete this attack at will. The attack does not require the ability to create objects. If server settings include `max_worker_processes`=0, the known versions of this attack are infeasible. However, undiscovered variants of the attack may be independent of that setting.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2001857
- https://security.gentoo.org/glsa/202211-04
- https://security.netapp.com/advisory/ntap-20220407-0008/
- https://www.postgresql.org/support/security/CVE-2021-3677/
