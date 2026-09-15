# [C] CVE-2019-16225

## Summary
Severity: Critical
Advisory: CVE-2019-16225
Aliases: GHSA-c74c-p4p7-r8q5, PYSEC-2019-237
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16225
Type: osv

## Details
An issue was discovered in py-lmdb 0.97. For certain values of mp_flags, mdb_page_touch does not properly set up mc->mc_pg[mc->top], leading to an invalid write operation. NOTE: this outcome occurs when accessing a data.mdb file supplied by an attacker.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/lmdb/lmdb%20write%20to%20illegal%20address
