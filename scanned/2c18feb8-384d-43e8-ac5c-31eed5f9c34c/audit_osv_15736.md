# [H] CVE-2019-19272

## Summary
Severity: High
Advisory: CVE-2019-19272
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-19272
Type: osv

## Details
An issue was discovered in tls_verify_crl in ProFTPD before 1.3.6. Direct dereference of a NULL pointer (a variable initialized to NULL) leads to a crash when validating the certificate of a client connecting to the server in a TLS client/server mutual-authentication setup.

## References
- https://github.com/proftpd/proftpd/issues/858
