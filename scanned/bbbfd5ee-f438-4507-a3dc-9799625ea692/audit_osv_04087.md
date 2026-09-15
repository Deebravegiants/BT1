# [H] Apache HTTP Server: DoS in HTTP/2 with initial windows size 0

## Summary
Severity: High
Advisory: BIT-apache-2023-43622
Aliases: CVE-2023-43622
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2023-43622
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.55 <2.4.58

## Details
An attacker, opening a HTTP/2 connection with an initial window size of 0, was able to block handling of that connection indefinitely in Apache HTTP Server. This could be used to exhaust worker resources in the server, similar to the well known "slow loris" attack pattern.
This has been fixed in version 2.4.58, so that such connection are terminated properly after the configured connection timeout.

This issue affects Apache HTTP Server: from 2.4.55 through 2.4.57.

Users are recommended to upgrade to version 2.4.58, which fixes the issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.netapp.com/advisory/ntap-20231027-0011/
- https://nvd.nist.gov/vuln/detail/CVE-2023-43622
