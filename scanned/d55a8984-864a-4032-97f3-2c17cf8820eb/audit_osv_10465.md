# [C] CVE-2017-15896

## Summary
Severity: Critical
Advisory: CVE-2017-15896
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-15896
Type: osv

## Details
Node.js was affected by OpenSSL vulnerability CVE-2017-3737 in regards to the use of SSL_read() due to TLS handshake failure. The result was that an active network attacker could send application data to Node.js using the TLS or HTTP2 modules in a way that bypassed TLS authentication and encryption.

## References
- https://nodejs.org/en/blog/vulnerability/december-2017-security-releases/
