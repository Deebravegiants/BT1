# [H] CVE-2020-17443

## Summary
Severity: High
Advisory: CVE-2020-17443
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17443
Type: osv

## Details
An issue was discovered in picoTCP 1.7.0. The code for creating an ICMPv6 echo replies doesn't check whether the ICMPv6 echo request packet's size is shorter than 8 bytes. If the size of the incoming ICMPv6 request packet is shorter than this, the operation that calculates the size of the ICMPv6 echo replies has an integer wrap around, leading to memory corruption and, eventually, Denial-of-Service in pico_icmp6_send_echoreply_not_frag in pico_icmp6.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
