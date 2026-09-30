# [M] Vertx gRPC server does not limit the maximum message size

## Summary
Severity: Medium
Advisory: GHSA-g76f-gjfx-4rpr
CVE: CVE-2024-8391
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-09-04
Source: https://github.com/advisories/GHSA-g76f-gjfx-4rpr
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-grpc-server` — affected >=4.3.0 <4.5.10
- Maven: `io.vertx:vertx-grpc-client` — affected >=4.3.0 <4.5.10

## Details
In Eclipse Vert.x version 4.3.0 to 4.5.9, the gRPC server does not limit the maximum length of message payload (Maven GAV: io.vertx:vertx-grpc-server and io.vertx:vertx-grpc-client). 

This is fixed in the 4.5.10 version. 

Note this does not affect the Vert.x gRPC server based grpc-java and Netty libraries (Maven GAV: io.vertx:vertx-grpc)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8391
- https://github.com/eclipse-vertx/vertx-grpc/issues/113
- https://github.com/eclipse-vertx/vertx-grpc/commit/a76b14a92410c89fcc590c5852d800b565916ccf
- https://github.com/eclipse-vertx/vertx-grpc
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/31
