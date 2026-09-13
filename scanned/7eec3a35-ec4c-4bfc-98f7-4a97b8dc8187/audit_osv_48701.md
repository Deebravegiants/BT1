# [M] CVE-2018-11723

## Summary
Severity: Medium
Advisory: CVE-2018-11723
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-11723
Type: osv

## Details
The libpff_name_to_id_map_entry_read function in libpff_name_to_id_map.c in libyal libpff through 2018-04-28 allows remote attackers to cause an information disclosure (heap-based buffer over-read) via a crafted pff file. NOTE: the vendor has disputed this as described in libyal/libpff issue 66 on GitHub

## References
- http://packetstormsecurity.com/files/148113/libpff-2018-04-28-Information-Disclosure.html
- http://seclists.org/fulldisclosure/2018/Jun/15
