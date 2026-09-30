# [M] CVE-2017-13099

## Summary
Severity: Medium
Advisory: CVE-2017-13099
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-13
Source: https://osv.dev/vulnerability/CVE-2017-13099
Type: osv

## Details
wolfSSL prior to version 3.12.2 provides a weak Bleichenbacher oracle when any TLS cipher suite using RSA key exchange is negotiated. An attacker can recover the private key from a vulnerable wolfSSL application. This vulnerability is referred to as "ROBOT."

## References
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2018-002.txt
- https://cert-portal.siemens.com/productcert/pdf/ssa-464260.pdf
- http://www.kb.cert.org/vuls/id/144389
- http://www.securityfocus.com/bid/102174
- https://robotattack.org/
- https://github.com/wolfSSL/wolfssl/pull/1229
