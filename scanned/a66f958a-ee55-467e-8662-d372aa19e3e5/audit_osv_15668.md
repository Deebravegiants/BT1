# [C] CVE-2019-18609

## Summary
Severity: Critical
Advisory: CVE-2019-18609
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-01
Source: https://osv.dev/vulnerability/CVE-2019-18609
Type: osv

## Details
An issue was discovered in amqp_handle_input in amqp_connection.c in rabbitmq-c 0.9.0. There is an integer overflow that leads to heap memory corruption in the handling of CONNECTION_STATE_HEADER. A rogue server could return a malicious frame header that leads to a smaller target_size value than needed. This condition is then carried on to a memcpy function that copies too much data into a heap buffer.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WA7CPNVYMF6OQNIYNLWUY6U2GTKFOKH3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XQER6XTKYMHNQR7QTHW7DJAH645WQROU/
- https://github.com/alanxz/rabbitmq-c/blob/master/ChangeLog.md
- https://lists.debian.org/debian-lts-announce/2019/12/msg00004.html
- https://security.gentoo.org/glsa/202003-07
- https://usn.ubuntu.com/4214-1/
- https://usn.ubuntu.com/4214-2/
- https://news.ycombinator.com/item?id=21681976
- https://github.com/alanxz/rabbitmq-c/commit/fc85be7123050b91b054e45b91c78d3241a5047a
