# [M] CVE-2018-18409

## Summary
Severity: Medium
Advisory: CVE-2018-18409
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-18409
Type: osv

## Details
A stack-based buffer over-read exists in setbit() at iptree.h of TCPFLOW 1.5.0, due to received incorrect values causing incorrect computation, leading to denial of service during an address_histogram call or a get_histogram call.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K6MP4YMCJX4ITOBFX427UMOA6E7ZLJDE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MN5FW6HKPDP7PI2IVNMFSQVIDSCQ5BOR/
- https://usn.ubuntu.com/3955-1/
- https://github.com/simsong/tcpflow/issues/195
