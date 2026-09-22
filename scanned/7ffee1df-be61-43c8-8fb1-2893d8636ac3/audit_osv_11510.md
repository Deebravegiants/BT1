# [C] CVE-2017-8289

## Summary
Severity: Critical
Advisory: CVE-2017-8289
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8289
Type: osv

## Details
Stack-based buffer overflow in the ipv6_addr_from_str function in sys/net/network_layer/ipv6/addr/ipv6_addr_from_str.c in RIOT prior to 2017-04-25 allows local attackers, and potentially remote attackers, to cause a denial of service or possibly have unspecified other impact via a malformed IPv6 address.

## References
- https://github.com/RIOT-OS/RIOT/issues/6840
- https://github.com/RIOT-OS/RIOT/pull/6961
- https://github.com/RIOT-OS/RIOT/pull/6962
