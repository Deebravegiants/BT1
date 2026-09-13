# [M] Remote Memory Exposure in mongoose

## Summary
Severity: Medium
Advisory: GHSA-r5xw-q988-826m
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-r5xw-q988-826m
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=3.5.5 <3.8.39
- npm: `mongoose` — affected >=4.0.0 <4.3.6

## Details
Versions of `mongoose` before 4.3.6, 3.8.39 are vulnerable to remote memory exposure.

Trying to save a number to a field of type Buffer on the affected mongoose versions allocates a chunk of uninitialized memory and stores it in the database.


## Recommendation

Update to version 4.3.6, 3.8.39 or later.

## References
- https://github.com/Automattic/mongoose/issues/3764
- https://gist.github.com/ChALkeR/440bc3dfcbd9b6da75c3
- https://gist.github.com/ChALkeR/d4a8055625221b6e65f0
- https://www.npmjs.com/advisories/599
