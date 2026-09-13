# [H] CVE-2020-27222

## Summary
Severity: High
Advisory: CVE-2020-27222
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-03
Source: https://osv.dev/vulnerability/CVE-2020-27222
Type: osv

## Details
In Eclipse Californium version 2.3.0 to 2.6.0, the certificate based (x509 and RPK) DTLS handshakes accidentally fails, because the DTLS server side sticks to a wrong internal state. That wrong internal state is set by a previous certificate based DTLS handshake failure with TLS parameter mismatch. The DTLS server side must be restarted to recover this. This allow clients to force a DoS.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=570844
