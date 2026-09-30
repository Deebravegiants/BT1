# [C] ALPINE-CVE-2019-17041

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-17041
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17041
Type: osv

## Affected
- Alpine:v3.10: `rsyslog` — affected >=0 <8.1904.0-r1
- Alpine:v3.11: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.12: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.13: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.14: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.15: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.16: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.17: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.18: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.19: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.20: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.21: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.22: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.23: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.24: `rsyslog` — affected >=0 <8.1908.0-r1
- Alpine:v3.7: `rsyslog` — affected >=0 <8.31.0-r1
- Alpine:v3.8: `rsyslog` — affected >=0 <8.34.0-r1
- Alpine:v3.9: `rsyslog` — affected >=0 <8.40.0-r4

## Details
An issue was discovered in Rsyslog v8.1908.0. contrib/pmaixforwardedfrom/pmaixforwardedfrom.c has a heap overflow in the parser for AIX log messages. The parser tries to locate a log message delimiter (in this case, a space or a colon) but fails to account for strings that do not satisfy this constraint. If the string does not match, then the variable lenMsg will reach the value zero and will skip the sanity check that detects invalid log messages. The message will then be considered valid, and the parser will eat up the nonexistent colon delimiter. In doing so, it will decrement lenMsg, a signed integer, whose value was zero and now becomes minus one. The following step in the parser is to shift left the contents of the message. To do this, it will call memmove with the right pointers to the target and destination strings, but the lenMsg will now be interpreted as a huge value, causing a heap overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17041
