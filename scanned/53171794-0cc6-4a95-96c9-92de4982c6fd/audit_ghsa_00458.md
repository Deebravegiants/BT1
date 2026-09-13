# [C] Eclipse Vert.x does not properly neutralize '' (forward slashes) sequences that can resolve to an external location

## Summary
Severity: Critical
Advisory: GHSA-h39x-m55c-v55h
CVE: CVE-2018-12542
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-h39x-m55c-v55h
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-web` — affected >=3.0.0 <3.5.4

## Details
In version from 3.0.0 to 3.5.3 of Eclipse Vert.x, the StaticHandler uses external input to construct a pathname that should be within a restricted directory, but it does not properly neutralize '\' (forward slashes) sequences that can resolve to a location that is outside of that directory when running on Windows Operating Systems.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12542
- https://github.com/vert-x3/vertx-web/issues/1025
- https://github.com/vert-x3/vertx-web/commit/57a65dce6f4c5aa5e3ce7288685e7f3447eb8f3b
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=539171
- https://github.com/advisories/GHSA-h39x-m55c-v55h
- https://github.com/vert-x3/vertx-web
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
