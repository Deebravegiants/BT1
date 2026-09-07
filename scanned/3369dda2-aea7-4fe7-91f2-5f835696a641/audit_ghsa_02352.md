# [H] Use after free in internment

## Summary
Severity: High
Advisory: GHSA-96w3-p368-4h8c
CVE: CVE-2020-35874
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-96w3-p368-4h8c
Type: github-advisory

## Affected
- crates.io: `internment` — affected >=0.3.12 <0.4.0

## Details
ArcIntern::drop has a race condition where it can release memory which is about to get another user. The new user will get a reference to freed memory.

This was fixed by serializing access to an interned object while it is being deallocated.

Versions prior to 0.3.12 used stronger locking which avoided the problem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35874
- https://github.com/droundy/internment/issues/11
- https://github.com/droundy/internment
- https://rustsec.org/advisories/RUSTSEC-2020-0017.html
