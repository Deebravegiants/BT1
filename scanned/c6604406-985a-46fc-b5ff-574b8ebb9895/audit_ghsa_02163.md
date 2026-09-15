# [H] Use after free in Rocket

## Summary
Severity: High
Advisory: GHSA-vcw4-8ph6-7vw8
CVE: CVE-2021-29935
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vcw4-8ph6-7vw8
Type: github-advisory

## Affected
- crates.io: `rocket` — affected >=0 <0.4.7

## Details
Affected versions of this crate transmuted a &str to a &'static str before pushing it into a StackVec, this value was then popped later in the same function.

This was assumed to be safe because the reference would be valid while the method's stack was active. In between the push and the pop, however, a function f was called that could invoke a user provided function.

If the user provided panicked, then the assumption used by the function was no longer true and the transmute to &'static would create an illegal static reference to the string. This could result in a freed string being used during (such as in a Drop implementation) or after (e.g through catch_unwind) the panic unwinding.

This flaw was corrected in commit `e325e2f` by using a guard object to ensure that the &'static str was dropped inside the function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29935
- https://github.com/SergioBenitez/Rocket/issues/1534
- https://github.com/SergioBenitez/Rocket/commit/b53a906a8e170fe9b151381c66a76a872c419f9e
- https://github.com/SergioBenitez/Rocket/commit/e325e2fce4d9f9f392761e9fb58b418a48cef8bb
- https://github.com/SergioBenitez/Rocket
- https://rustsec.org/advisories/RUSTSEC-2021-0044.html
