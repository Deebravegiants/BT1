# [C] CVE-2019-13951

## Summary
Severity: Critical
Advisory: CVE-2019-13951
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-13951
Type: osv

## Details
The set_ipv4() function in zscan_rfc1035.rl in gdnsd 3.x before 3.2.1 has a stack-based buffer overflow via a long and malformed IPv4 address in zone data.

## References
- https://github.com/gdnsd/gdnsd/issues/185
