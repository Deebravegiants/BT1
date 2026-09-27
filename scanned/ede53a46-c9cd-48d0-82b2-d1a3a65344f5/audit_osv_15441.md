# [C] CVE-2019-16227

## Summary
Severity: Critical
Advisory: CVE-2019-16227
Aliases: GHSA-pf3p-v9xp-mrvf, PYSEC-2019-239
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16227
Type: osv

## Details
An issue was discovered in py-lmdb 0.97. For certain values of mn_flags, mdb_cursor_set triggers a memcpy with an invalid write operation within mdb_xcursor_init1. NOTE: this outcome occurs when accessing a data.mdb file supplied by an attacker.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/lmdb/lmdb%20memcpy%20illegal%20dst
