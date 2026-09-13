# [C] CVE-2021-26707

## Summary
Severity: Critical
Advisory: CVE-2021-26707
Aliases: GHSA-r6rj-9ch6-g264
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-26707
Type: osv

## Details
The merge-deep library before 3.0.3 for Node.js can be tricked into overwriting properties of Object.prototype or adding new properties to it. These properties are then inherited by every object in the program, thus facilitating prototype-pollution attacks against applications using this library.

## References
- https://security.netapp.com/advisory/ntap-20210716-0008/
- https://securitylab.github.com/advisories/GHSL-2020-160-merge-deep/
- https://www.npmjs.com/package/merge-deep
- https://github.com/jonschlinkert/merge-deep/commit/11e5dd56de8a6aed0b1ed022089dbce6968d82a5
