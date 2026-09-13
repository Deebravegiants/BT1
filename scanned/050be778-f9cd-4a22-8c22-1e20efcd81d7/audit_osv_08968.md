# [C] CVE-2016-7115

## Summary
Severity: Critical
Advisory: CVE-2016-7115
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-30
Source: https://osv.dev/vulnerability/CVE-2016-7115
Type: osv

## Details
Buffer overflow in the handle_packet function in mactelnet.c in the client in MAC-Telnet 0.4.3 and earlier allows remote TELNET servers to execute arbitrary code via a long string in an MT_CPTYPE_PASSSALT control packet.

## References
- http://www.securityfocus.com/bid/92699
- https://github.com/haakonnessjoen/MAC-Telnet/commit/b69d11727d4f0f8cf719c79e3fb700f55ca03e9a
- https://github.com/haakonnessjoen/MAC-Telnet/pull/20
