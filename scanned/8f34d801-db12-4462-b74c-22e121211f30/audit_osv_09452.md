# [H] CVE-2016-9917

## Summary
Severity: High
Advisory: CVE-2016-9917
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-9917
Type: osv

## Details
In BlueZ 5.42, a buffer overflow was observed in "read_n" function in "tools/hcidump.c" source file. This issue can be triggered by processing a corrupted dump file and will result in hcidump crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00069.html
- http://www.securityfocus.com/bid/95013
- https://www.spinics.net/lists/linux-bluetooth/msg68892.html
