# [C] Path Traversal in Eclipse Vert

## Summary
Severity: Critical
Advisory: GHSA-vjw7-6gfq-6wf5
CVE: CVE-2019-17640
CWE: CWE-22, CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-vjw7-6gfq-6wf5
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-web` — affected >=3.0.0 <3.9.4

## Details
In Eclipse Vert.x 3.4.x up to 3.9.4, 4.0.0-milestone1, 4.0.0-milestone2, 4.0.0-milestone3, 4.0.0-milestone4, 4.0.0-milestone5, 4.0.0.Beta1, 4.0.0.Beta2, and 4.0.0.Beta3, StaticHandler doesn't correctly processes back slashes on Windows Operating systems, allowing, escape the webroot folder to the current working directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17640
- https://github.com/vert-x3/vertx-web/commit/b12f7c4c6576a8adc3f683b2899de4b0e7d099e4
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=567416
- https://lists.apache.org/thread.html/r591f6932560c8c46cee87415afed92924a982189fea7f7c9096f8e33@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r8383b5e7344a8b872e430ad72241b84b83e9701d275c602cfe34a941@%3Ccommits.servicecomb.apache.org%3E
- https://lists.apache.org/thread.html/r8d863b148efe778ce5f8f961d0cafeda399e681d3f0656233b4c5511@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rfd0ebf8387cfd0b959d1e218797e709793cce51a5ea2f84d0976f47d@%3Ccommits.pulsar.apache.org%3E
- https://mvnrepository.com/artifact/io.vertx/vertx-web
