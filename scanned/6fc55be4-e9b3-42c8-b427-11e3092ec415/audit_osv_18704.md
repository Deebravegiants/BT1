# [M] CVE-2020-35518

## Summary
Severity: Medium
Advisory: CVE-2020-35518
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2020-35518
Type: osv

## Details
When binding against a DN during authentication, the reply from 389-ds-base will be different whether the DN exists or not. This can be used by an unauthenticated attacker to check the existence of an entry in the LDAP database.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1905565
- https://github.com/389ds/389-ds-base/commit/b6aae4d8e7c8a6ddd21646f94fef1bf7f22c3f32
- https://github.com/389ds/389-ds-base/commit/cc0f69283abc082488824702dae485b8eae938bc
- https://github.com/389ds/389-ds-base/issues/4480
