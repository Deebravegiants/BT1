# [M] CVE-2019-11638

## Summary
Severity: Medium
Advisory: CVE-2019-11638
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-05-01
Source: https://osv.dev/vulnerability/CVE-2019-11638
Type: osv

## Details
An issue was discovered in GNU recutils 1.8. There is a NULL pointer dereference in the function rec_field_name_equal_p at rec-field-name.c in librec.a, leading to a crash.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/recutils/bug-report-recutils/rec2csv
- https://github.com/TeamSeri0us/pocs/blob/master/recutils/bug-report-recutils
