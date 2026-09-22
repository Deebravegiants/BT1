# [M] wallabag subject to Improper Authorization via annotations

## Summary
Severity: Medium
Advisory: GHSA-mrqx-mjc4-vfh3
CVE: CVE-2023-0610
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-mrqx-mjc4-vfh3
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=2.0.0-beta.1 <2.5.3

## Details
### Impact
The annotations feature lets users add annotations on highlighted parts of an entry.

The controller does not validate authorization on `PUT` and `DELETE` requests which lets a logged user modify or delete any annotation using their ID on their endpoints `example.org/annotations/{id}`.

These vulnerable requests also disclose highlighted parts of the entry to the attacker.

You should immediately patch your instance to version 2.5.3 or higher if you have more than one user and/or having open registration.

### Resolution

A user check is now done in the vulnerable methods before applying change on an annotation.

The Annotation retrieval through a `ParamConverter` has also been replaced with a call to the `AnnotationRepository` in order to prevent any information disclosure through response discrepancy.

### Workarounds



### Credits

We would like to thank @bAuh0lz for reporting this issue through huntr.dev.

Reference: https://huntr.dev/bounties/8fdd9b31-d89b-4bbe-9557-20b960faf926/

## References
- https://github.com/wallabag/wallabag/security/advisories/GHSA-mrqx-mjc4-vfh3
- https://nvd.nist.gov/vuln/detail/CVE-2023-0610
- https://github.com/wallabag/wallabag/commit/5ac6b6bff9e2e3a87fd88c2904ff3c6aac40722e
- https://github.com/wallabag/wallabag
- https://huntr.dev/bounties/8fdd9b31-d89b-4bbe-9557-20b960faf926
