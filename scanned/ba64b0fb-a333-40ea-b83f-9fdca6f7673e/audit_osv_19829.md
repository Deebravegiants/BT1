# [C] CVE-2021-26529

## Summary
Severity: Critical
Advisory: CVE-2021-26529
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-26529
Type: osv

## Details
The mg_tls_init function in Cesanta Mongoose HTTPS server 7.0 and 6.7-6.18 (compiled with mbedTLS support) is vulnerable to remote OOB write attack via connection request after exhausting memory pool.

## References
- https://github.com/cesanta/mongoose/issues/1203
