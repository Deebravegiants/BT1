# [C] CVE-2017-5640

## Summary
Severity: Critical
Advisory: CVE-2017-5640
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-5640
Type: osv

## Details
It was noticed that a malicious process impersonating an Impala daemon in Apache Impala (incubating) 2.7.0 to 2.8.0 could cause Impala daemons to skip authentication checks when Kerberos is enabled (but TLS is not). If the malicious server responds with 'COMPLETE' before the SASL handshake has completed, the client will consider the handshake as completed even though no exchange of credentials has happened.

## References
- https://lists.apache.org/thread.html/c02e83aa46c90b7cbc87dd649cf8f9b73e11053eddea9144a397da53%40%3Cdev.impala.apache.org%3E
- http://www.securityfocus.com/bid/99508
