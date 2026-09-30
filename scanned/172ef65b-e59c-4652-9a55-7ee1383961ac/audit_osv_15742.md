# [C] CVE-2019-19317

## Summary
Severity: Critical
Advisory: CVE-2019-19317
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-05
Source: https://osv.dev/vulnerability/CVE-2019-19317
Type: osv

## Details
lookupName in resolve.c in SQLite 3.30.1 omits bits from the colUsed bitmask in the case of a generated column, which allows attackers to cause a denial of service or possibly have unspecified other impact.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://security.netapp.com/advisory/ntap-20191223-0001/
- https://github.com/sqlite/sqlite/commit/522ebfa7cee96fb325a22ea3a2464a63485886a8
- https://github.com/sqlite/sqlite/commit/73bacb7f93eab9f4bd5a65cbc4ae242acf63c9e3
- https://www.oracle.com/security-alerts/cpuapr2020.html
