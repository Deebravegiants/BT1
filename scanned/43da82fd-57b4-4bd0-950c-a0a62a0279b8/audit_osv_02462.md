# [H] ALPINE-CVE-2022-24903

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24903
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24903
Type: osv

## Affected
- Alpine:v3.12: `rsyslog` — affected >=0 <8.2004.0-r2
- Alpine:v3.13: `rsyslog` — affected >=0 <8.2012.0-r3
- Alpine:v3.14: `rsyslog` — affected >=0 <8.2012.0-r3
- Alpine:v3.15: `rsyslog` — affected >=0 <8.2108.0-r2
- Alpine:v3.16: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.17: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.18: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.19: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.20: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.21: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.22: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.23: `rsyslog` — affected >=0 <8.2204.1-r0
- Alpine:v3.24: `rsyslog` — affected >=0 <8.2204.1-r0

## Details
Rsyslog is a rocket-fast system for log processing. Modules for TCP syslog reception have a potential heap buffer overflow when octet-counted framing is used. This can result in a segfault or some other malfunction. As of our understanding, this vulnerability can not be used for remote code execution. But there may still be a slight chance for experts to do that. The bug occurs when the octet count is read. While there is a check for the maximum number of octets, digits are written to a heap buffer even when the octet count is over the maximum, This can be used to overrun the memory buffer. However, once the sequence of digits stop, no additional characters can be added to the buffer. In our opinion, this makes remote exploits impossible or at least highly complex. Octet-counted framing is one of two potential framing modes. It is relatively uncommon, but enabled by default on receivers. Modules `imtcp`, `imptcp`, `imgssapi`, and `imhttp` are used for regular syslog message reception. It is best practice not to directly expose them to the public. When this practice is followed, the risk is considerably lower. Module `imdiag` is a diagnostics module primarily intended for testbench runs. We do not expect it to be present on any production installation. Octet-counted framing is not very common. Usually, it needs to be specifically enabled at senders. If users do not need it, they can turn it off for the most important modules. This will mitigate the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24903
