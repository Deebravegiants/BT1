# [C] CVE-2019-17041

## Summary
Severity: Critical
Advisory: CVE-2019-17041
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-07
Source: https://osv.dev/vulnerability/CVE-2019-17041
Type: osv

## Details
An issue was discovered in Rsyslog v8.1908.0. contrib/pmaixforwardedfrom/pmaixforwardedfrom.c has a heap overflow in the parser for AIX log messages. The parser tries to locate a log message delimiter (in this case, a space or a colon) but fails to account for strings that do not satisfy this constraint. If the string does not match, then the variable lenMsg will reach the value zero and will skip the sanity check that detects invalid log messages. The message will then be considered valid, and the parser will eat up the nonexistent colon delimiter. In doing so, it will decrement lenMsg, a signed integer, whose value was zero and now becomes minus one. The following step in the parser is to shift left the contents of the message. To do this, it will call memmove with the right pointers to the target and destination strings, but the lenMsg will now be interpreted as a huge value, causing a heap overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KPNCHI7X2IEXRH6RYD6IDPR4PLB5RPC7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W6SUQE25RD37CD24BHKUWMG27U5RQ2FU/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00032.html
- https://github.com/rsyslog/rsyslog/blob/v8-stable/ChangeLog
- https://lists.debian.org/debian-lts-announce/2021/11/msg00030.html
- https://github.com/rsyslog/rsyslog/pull/3884
