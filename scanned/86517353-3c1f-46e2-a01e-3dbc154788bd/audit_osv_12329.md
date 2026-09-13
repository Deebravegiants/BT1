# [H] CVE-2018-11364

## Summary
Severity: High
Advisory: CVE-2018-11364
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11364
Type: osv

## Details
sav_parse_machine_integer_info_record in spss/readstat_sav_read.c in libreadstat.a in ReadStat 0.1.1 has a memory leak related to an iconv_open call.

## References
- https://github.com/ChijinZ/security_advisories/tree/master/ReadStat-7bced5b
