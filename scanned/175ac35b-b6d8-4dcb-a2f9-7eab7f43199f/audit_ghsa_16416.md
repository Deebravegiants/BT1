# [C] SQLAlchemyDA unauthenticated arbitrary SQL query execution

## Summary
Severity: Critical
Advisory: GHSA-r3jc-3qmm-w3pw
CVE: CVE-2024-24811
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-r3jc-3qmm-w3pw
Type: github-advisory

## Affected
- PyPI: `Products.SQLAlchemyDA` — affected >=0 <2.2

## Details
### Impact
The vulnerability allows unauthenticated execution of arbitrary SQL statements on the database the SQLAlchemyDA instance is connected to. All users are affected.

### Patches
The problem has been patched in version 2.2. 

### Workarounds
There is no workaround. All users are urged to upgrade to version 2.2

## References
- https://github.com/zopefoundation/Products.SQLAlchemyDA/security/advisories/GHSA-r3jc-3qmm-w3pw
- https://nvd.nist.gov/vuln/detail/CVE-2024-24811
- https://github.com/zopefoundation/Products.SQLAlchemyDA/commit/e682b99f8406f20bc3f0f2c77153ed7345fd215a
- https://github.com/zopefoundation/Products.SQLAlchemyDA
