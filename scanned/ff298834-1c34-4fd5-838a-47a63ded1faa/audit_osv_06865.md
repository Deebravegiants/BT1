# [C] MongoDB Server may allow successful untrusted connection

## Summary
Severity: Critical
Advisory: BIT-mongodb-2024-1351
Aliases: CVE-2024-1351
Ecosystem: Bitnami
Published: 2025-03-12
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-1351
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.0.0 <7.0.7

## Details
Under certain configurations of --tlsCAFile and tls.CAFile, MongoDB Server may skip peer certificate validation which may result in untrusted connections to succeed. This may effectively reduce the security guarantees provided by TLS and open connections  that should have been closed due to failing certificate validation. This issue affects MongoDB Server v7.0 versions prior to and including 7.0.5, MongoDB Server v6.0 versions prior to and including 6.0.13, MongoDB Server v5.0 versions prior to and including 5.0.24 and MongoDB Server v4.4 versions prior to and including 4.4.28.

Required Configuration : A server process will allow incoming connections to skip peer certificate validation if the server process was started with TLS enabled (net.tls.mode set to allowTLS, preferTLS, or requireTLS) and without a net.tls.CAFile configured.

## References
- https://jira.mongodb.org/browse/SERVER-72839
- https://security.netapp.com/advisory/ntap-20240524-0010/
- https://www.mongodb.com/docs/manual/release-notes/4.4/#4.4.29---february-28--2024
- https://www.mongodb.com/docs/manual/release-notes/7.0/#7.0.6---feb-28--2024
- https://www.mongodb.com/docs/v5.0/release-notes/5.0/#5.0.25---february-28--2024
- https://www.mongodb.com/docs/v6.0/release-notes/6.0/#6.0.14---feb-28--2024
- https://nvd.nist.gov/vuln/detail/CVE-2024-1351
