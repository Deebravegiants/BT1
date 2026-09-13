# [C] CVE-2015-8366

## Summary
Severity: Critical
Advisory: CVE-2015-8366
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-14
Source: https://osv.dev/vulnerability/CVE-2015-8366
Type: osv

## Details
Array index error in smal_decode_segment function in LibRaw before 0.17.1 allows context-dependent attackers to cause memory errors and possibly execute arbitrary code via vectors related to indexes.

## References
- http://packetstormsecurity.com/files/134573/LibRaw-0.17-Overflow.html
- http://seclists.org/fulldisclosure/2015/Nov/108
- http://www.libraw.org/news/libraw-0-17-1
- http://seclists.org/fulldisclosure/2015/Nov/108
