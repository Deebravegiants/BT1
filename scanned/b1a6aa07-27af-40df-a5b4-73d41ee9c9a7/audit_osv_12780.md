# [C] CVE-2018-14767

## Summary
Severity: Critical
Advisory: CVE-2018-14767
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-31
Source: https://osv.dev/vulnerability/CVE-2018-14767
Type: osv

## Details
In Kamailio before 5.0.7 and 5.1.x before 5.1.4, a crafted SIP message with a double "To" header and an empty "To" tag causes a segmentation fault and crash. The reason is missing input validation in the "build_res_buf_from_sip_req" core function. This could result in denial of service and potentially the execution of arbitrary code.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00018.html
- https://www.debian.org/security/2018/dsa-4267
- https://skalatan.de/blog/advisory-hw-2018-05
