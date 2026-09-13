# [H] CVE-2018-20230

## Summary
Severity: High
Advisory: CVE-2018-20230
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-19
Source: https://osv.dev/vulnerability/CVE-2018-20230
Type: osv

## Details
An issue was discovered in PSPP 1.2.0. There is a heap-based buffer overflow at the function read_bytes_internal in utilities/pspp-dump-sav.c, which allows attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1660318
