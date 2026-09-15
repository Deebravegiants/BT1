# [H] CVE-2017-7243

## Summary
Severity: High
Advisory: CVE-2017-7243
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2017-7243
Type: osv

## Details
Eclipse tinydtls 0.8.2 for Eclipse IoT allows remote attackers to cause a denial of service (DTLS peer crash) by sending a "Change cipher spec" packet without pre-handshake.

## References
- http://www.securityfocus.com/bid/97193
- https://gist.github.com/k1rh4/25dcb124aef2a8a2a5f4677d64d1998b
- https://github.com/k1rh4/CVE/blob/master/tinydtls
