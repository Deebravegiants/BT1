# [H] CVE-2026-57281

## Summary
Severity: High
Advisory: CVE-2026-57281
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57281
Type: osv

## Details
Jenkins Script Security Plugin 1402.v94c9ce464861 and earlier does not reject Groovy AST transformation annotations carrying an extensions member, allowing attackers able to run sandboxed Groovy scripts to execute code outside the sandbox if a suitable script is present on the classpath of the component that evaluates the script.

## References
- https://access.redhat.com/security/cve/CVE-2026-57281
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-57281.json
- https://access.redhat.com/errata/RHSA-2026:60239
- https://access.redhat.com/errata/RHSA-2026:60246
- https://access.redhat.com/errata/RHSA-2026:60247
- https://access.redhat.com/errata/RHSA-2026:60248
- https://access.redhat.com/errata/RHSA-2026:60249
- https://access.redhat.com/errata/RHSA-2026:60250
- https://access.redhat.com/errata/RHSA-2026:60251
- https://access.redhat.com/errata/RHSA-2026:60252
- https://access.redhat.com/errata/RHSA-2026:60254
- https://access.redhat.com/errata/RHSA-2026:60256
- https://access.redhat.com/errata/RHSA-2026:60259
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3793
- https://bugzilla.redhat.com/show_bug.cgi?id=2492200
