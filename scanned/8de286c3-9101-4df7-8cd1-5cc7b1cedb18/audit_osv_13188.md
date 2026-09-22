# [H] CVE-2018-18483

## Summary
Severity: High
Advisory: CVE-2018-18483
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-18483
Type: osv

## Details
The get_count function in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.31, allows remote attackers to cause a denial of service (malloc called with the result of an integer-overflowing calculation) or possibly have unspecified other impact via a crafted string, as demonstrated by c++filt.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/105689
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=87602
- https://sourceware.org/bugzilla/show_bug.cgi?id=23767
