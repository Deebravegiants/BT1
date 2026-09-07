# [H] Socket.IO-client Java before 2.0.1 vulnerable to NULL Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-85xx-xhjm-rhrw
CVE: CVE-2022-25867
CWE: CWE-476
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-03
Source: https://github.com/advisories/GHSA-85xx-xhjm-rhrw
Type: github-advisory

## Affected
- Maven: `io.socket:socket.io-client` — affected >=0 <2.0.1

## Details
The package io.socket:socket.io-client before 2.0.1 is vulnerable to NULL Pointer Dereference when parsing a packet with with invalid payload format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25867
- https://github.com/socketio/socket.io-client-java/issues/508%23issuecomment-1179817361
- https://github.com/socketio/socket.io-client-java/commit/8664499b6f31154f49783531f778dac5387b766b
- https://github.com/socketio/socket.io-client-java/commit/e8ffe9d1383736f6a21090ab959a2f4fa5a41284
- https://github.com/socketio/socket.io-client-java
- https://github.com/socketio/socket.io-client-java/releases/tag/socket.io-client-2.0.1
- https://security.snyk.io/vuln/SNYK-JAVA-IOSOCKET-2949738
