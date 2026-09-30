# [H] CVE-2021-37625

## Summary
Severity: High
Advisory: CVE-2021-37625
Aliases: GHSA-q27r-h25m-hcc7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-37625
Type: osv

## Details
Skytable is an open source NoSQL database. In versions prior to 0.6.4 an incorrect check of return value of the accept function in the run-loop for a TCP socket/TLS socket/TCP+TLS multi-socket causes an early exit from the run loop that should continue infinitely unless terminated by a local user, effectively causing the whole database server to shut down. This has severe impact and can be used to easily cause DoS attacks without the need to use much bandwidth. The attack vectors include using an incomplete TLS connection for example by not providing the certificate for the connection and using a specially crafted TCP packet that triggers the application layer backoff algorithm.

## References
- https://github.com/skytable/skytable/security/advisories/GHSA-q27r-h25m-hcc7
- https://github.com/skytable/skytable/commit/bb19d024ea1e5e0c9a3d75a9ee58ff03c70c7e5d
- https://security.skytable.io/ve/s/00002.html
