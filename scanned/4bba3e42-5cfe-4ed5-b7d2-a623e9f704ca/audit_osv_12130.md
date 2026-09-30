# [H] CVE-2018-1046

## Summary
Severity: High
Advisory: CVE-2018-1046
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2018-1046
Type: osv

## Details
pdns before version 4.1.2 is vulnerable to a buffer overflow in dnsreplay. In the dnsreplay tool provided with PowerDNS Authoritative, replaying a specially crafted PCAP file can trigger a stack-based buffer overflow, leading to a crash and potentially arbitrary code execution. This buffer overflow only occurs when the -ecs-stamp option of dnsreplay is used.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1046
