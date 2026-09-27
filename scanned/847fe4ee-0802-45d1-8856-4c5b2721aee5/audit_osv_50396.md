# [C] CVE-2020-14931

## Summary
Severity: Critical
Advisory: CVE-2020-14931
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-19
Source: https://osv.dev/vulnerability/CVE-2020-14931
Type: osv

## Details
A stack-based buffer overflow in DMitry (Deepmagic Information Gathering Tool) 1.3a might allow remote WHOIS servers to execute arbitrary code via a long line in a response that is mishandled by nic_format_buff.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00024.html
- https://github.com/jaygreig86/dmitry/issues/4
