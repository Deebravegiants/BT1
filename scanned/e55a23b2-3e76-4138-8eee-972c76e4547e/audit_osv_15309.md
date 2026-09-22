# [C] CVE-2019-15167

## Summary
Severity: Critical
Advisory: CVE-2019-15167
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-08-27
Source: https://osv.dev/vulnerability/CVE-2019-15167
Type: osv

## Details
The VRRP parser in tcpdump before 4.9.3 has a buffer over-read in print-vrrp.c:vrrp_print() for VRRP version 3, a different vulnerability than CVE-2018-14463.

## References
- https://github.com/the-tcpdump-group/tcpdump/commit/a152aebfd1114376ba266ed30416be596ef9d806
