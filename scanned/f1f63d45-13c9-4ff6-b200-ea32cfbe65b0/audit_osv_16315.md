# [H] CVE-2019-5163

## Summary
Severity: High
Advisory: CVE-2019-5163
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-5163
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the UDPRelay functionality of Shadowsocks-libev 3.3.2. When utilizing a Stream Cipher and a local_address, arbitrary UDP packets can cause a FATAL error code path and exit. An attacker can send arbitrary UDP packets to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00061.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0956
