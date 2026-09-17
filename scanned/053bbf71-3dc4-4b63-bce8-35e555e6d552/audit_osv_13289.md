# [C] CVE-2018-19115

## Summary
Severity: Critical
Advisory: CVE-2018-19115
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19115
Type: osv

## Details
keepalived before 2.0.7 has a heap-based buffer overflow when parsing HTTP status codes resulting in DoS or possibly unspecified other impact, because extract_status_code in lib/html.c has no validation of the status code and instead writes an unlimited amount of data to the heap.

## References
- https://usn.ubuntu.com/3995-1/
- https://usn.ubuntu.com/3995-2/
- https://access.redhat.com/errata/RHSA-2019:0022
- https://access.redhat.com/errata/RHSA-2019:1792
- https://access.redhat.com/errata/RHSA-2019:1945
- https://lists.debian.org/debian-lts-announce/2018/11/msg00034.html
- https://security.gentoo.org/glsa/201903-01
- https://bugzilla.suse.com/show_bug.cgi?id=1015141
- https://github.com/acassen/keepalived/pull/961
- https://github.com/acassen/keepalived/pull/961/commits/f28015671a4b04785859d1b4b1327b367b6a10e9
