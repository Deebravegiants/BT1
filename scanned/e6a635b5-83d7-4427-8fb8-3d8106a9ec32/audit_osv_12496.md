# [C] CVE-2018-12544

## Summary
Severity: Critical
Advisory: CVE-2018-12544
Aliases: GHSA-qh3m-qw6v-qvhg
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-10
Source: https://osv.dev/vulnerability/CVE-2018-12544
Type: osv

## Details
In version from 3.5.Beta1 to 3.5.3 of Eclipse Vert.x, the OpenAPI XML type validator creates XML parsers without taking appropriate defense against XML attacks. This mechanism is exclusively when the developer uses the Eclipse Vert.x OpenAPI XML type validator to validate a provided schema.

## References
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26%40%3Ccommits.pulsar.apache.org%3E
- https://access.redhat.com/errata/RHSA-2018:2946
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=539568
- https://github.com/vert-x3/vertx-web/issues/1021
