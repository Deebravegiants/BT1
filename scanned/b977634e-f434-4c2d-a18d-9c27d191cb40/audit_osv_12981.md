# [C] CVE-2018-16657

## Summary
Severity: Critical
Advisory: CVE-2018-16657
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-07
Source: https://osv.dev/vulnerability/CVE-2018-16657
Type: osv

## Details
In Kamailio before 5.0.7 and 5.1.x before 5.1.4, a crafted SIP message with an invalid Via header causes a segmentation fault and crashes Kamailio. The reason is missing input validation in the crcitt_string_array core function for calculating a CRC hash for To tags. (An additional error is present in the check_via_address core function: this function also misses input validation.) This could result in denial of service and potentially the execution of arbitrary code.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00013.html
- https://www.debian.org/security/2018/dsa-4292
- https://skalatan.de/blog/advisory-hw-2018-06
