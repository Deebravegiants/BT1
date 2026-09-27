# [H] High severity vulnerability that affects io.vertx:vertx-web

## Summary
Severity: High
Advisory: GHSA-rvgg-f8qm-6h7j
CVE: CVE-2018-12540
CWE: CWE-352
Ecosystem: Maven
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-rvgg-f8qm-6h7j
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-web` — affected >=3.0.0 <3.5.3

## Details
In version from 3.0.0 to 3.5.2 of Eclipse Vert.x, the CSRFHandler do not assert that the XSRF Cookie matches the returned XSRF header/form parameter. This allows replay attacks with previously issued tokens which are not expired yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12540
- https://github.com/vert-x3/vertx-web/issues/970
- https://github.com/vert-x3/vertx-web/commit/f42b193b15a29b772fc576b2d0f2497e7474a7e
- https://access.redhat.com/errata/RHSA-2018:2371
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=536948
- https://github.com/advisories/GHSA-rvgg-f8qm-6h7j
- https://github.com/vert-x3/vertx-web
- https://lists.apache.org/thread.html/r10aef585c521f8ef603f5831f9d97a27d920624025131da950e0c62f@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r3fffda8e947edaa359152c8dc4c4ea9c96fd8ced1999bbce92bc6b25@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r59482ebed302aa49ac7e0c51737499746b0d086fcdeb8f90e705951f@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rc5b4ae8a7caae6d3d5b3266cb050823b96dd62b30718b90b778d3d8b@%3Ccommits.pulsar.apache.org%3E
