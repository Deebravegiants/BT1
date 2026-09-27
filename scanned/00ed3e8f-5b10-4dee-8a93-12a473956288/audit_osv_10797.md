# [H] CVE-2017-2784

## Summary
Severity: High
Advisory: CVE-2017-2784
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2017-2784
Type: osv

## Details
An exploitable free of a stack pointer vulnerability exists in the x509 certificate parsing code of ARM mbed TLS before 1.3.19, 2.x before 2.1.7, and 2.4.x before 2.4.2. A specially crafted x509 certificate, when parsed by mbed TLS library, can cause an invalid free of a stack pointer leading to a potential remote code execution. In order to exploit this vulnerability, an attacker can act as either a client or a server on a network to deliver malicious x509 certificates to vulnerable applications.

## References
- https://security.gentoo.org/glsa/201706-18
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2017-01
- http://www.talosintelligence.com/reports/TALOS-2017-0274/
