# [M] CVE-2018-12096

## Summary
Severity: Medium
Advisory: CVE-2018-12096
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12096
Type: osv

## Details
The liblnk_data_string_get_utf8_string_size function in liblnk_data_string.c in liblnk through 2018-04-19 allows remote attackers to cause an information disclosure (heap-based buffer over-read) via a crafted lnk file. NOTE: the vendor has disputed this as described in libyal/liblnk issue 33 on GitHub

## References
- http://seclists.org/fulldisclosure/2018/Jun/33
