# [C] CVE-2020-27507

## Summary
Severity: Critical
Advisory: CVE-2020-27507
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2020-27507
Type: osv

## Details
The Kamailio SIP before 5.5.0 server mishandles INVITE requests with duplicated fields and overlength tag, leading to a buffer overflow that crashes the server or possibly have unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00030.html
- https://github.com/kamailio/kamailio/issues/2503
- https://github.com/kamailio/kamailio/commit/ada3701d22b1fd579f06b4f54fa695fa988e685f
