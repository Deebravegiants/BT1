# [M] CVE-2018-11727

## Summary
Severity: Medium
Advisory: CVE-2018-11727
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-11727
Type: osv

## Details
The libfsntfs_attribute_read_from_mft function in libfsntfs_attribute.c in libfsntfs through 2018-04-20 allows remote attackers to cause an information disclosure (heap-based buffer over-read) via a crafted ntfs file. NOTE: the vendor has disputed this as described in libyal/libfsntfs issue 8 on GitHub

## References
- http://packetstormsecurity.com/files/148115/libfsntfs-20180420-Information-Disclosure.html
- http://seclists.org/fulldisclosure/2018/Jun/17
