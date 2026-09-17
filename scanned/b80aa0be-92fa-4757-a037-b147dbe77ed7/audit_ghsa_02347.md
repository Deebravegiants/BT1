# [C] Double free in containers

## Summary
Severity: Critical
Advisory: GHSA-cv7x-6rc6-pq5v
CVE: CVE-2021-25907
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cv7x-6rc6-pq5v
Type: github-advisory

## Affected
- crates.io: `containers` — affected >=0 <0.9.11

## Details
Upon panic in a user-provided function f, fn mutate() & fn mutate2 drops twice a same object.

Affected versions of this crate did not guard against double drop while temporarily duplicating an object's ownership with ptr::read().

Dropping a same object can result in memory corruption.

The flaw was corrected in version "0.9.11" by fixing the code to abort upon panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25907
- https://github.com/strake/containers.rs/issues/2
- https://github.com/strake/containers.rs
- https://rustsec.org/advisories/RUSTSEC-2021-0010.html
