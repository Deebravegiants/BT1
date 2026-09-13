# [H] CVE-2021-34433

## Summary
Severity: High
Advisory: CVE-2021-34433
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-08-20
Source: https://osv.dev/vulnerability/CVE-2021-34433
Type: osv

## Details
In Eclipse Californium version 2.0.0 to 2.6.4 and 3.0.0-M1 to 3.0.0-M3, the certificate based (x509 and RPK) DTLS handshakes accidentally succeeds without verifying the server side's signature on the client side, if that signature is not included in the server's ServerKeyExchange.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=575281
