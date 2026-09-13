# [H] CVE-2019-19271

## Summary
Severity: High
Advisory: CVE-2019-19271
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-19271
Type: osv

## Details
An issue was discovered in tls_verify_crl in ProFTPD before 1.3.6. A wrong iteration variable, used when checking a client certificate against CRL entries (installed by a system administrator), can cause some CRL entries to be ignored, and can allow clients whose certificates have been revoked to proceed with a connection to the server.

## References
- https://github.com/proftpd/proftpd/issues/860
