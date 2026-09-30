# [H] CVE-2019-12760

## Summary
Severity: High
Advisory: CVE-2019-12760
Aliases: GHSA-22mf-97vh-x8rw, PYSEC-2019-109
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-06
Source: https://osv.dev/vulnerability/CVE-2019-12760
Type: osv

## Details
A deserialization vulnerability exists in the way parso through 0.4.0 handles grammar parsing from the cache. Cache loading relies on pickle and, provided that an evil pickle can be written to a cache grammar file and that its parsing can be triggered, this flaw leads to Arbitrary Code Execution. NOTE: This is disputed because "the cache directory is not under control of the attacker in any common configuration.

## References
- https://github.com/davidhalter/parso/issues/75
- https://gist.github.com/dhondta/f71ae7e5c4234f8edfd2f12503a5dcc7
