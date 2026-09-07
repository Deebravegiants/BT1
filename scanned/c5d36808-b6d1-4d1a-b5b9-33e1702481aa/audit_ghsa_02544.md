# [H] Integer Overflow/Infinite Loop in the http crate

## Summary
Severity: High
Advisory: GHSA-x7vr-c387-8w57
CVE: CVE-2020-25574
CWE: CWE-190, CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-x7vr-c387-8w57
Type: github-advisory

## Affected
- crates.io: `http` — affected >=0 <0.1.20

## Details
HeaderMap::reserve() used usize::next_power_of_two() to calculate the increased capacity. However, next_power_of_two() silently overflows to 0 if given a sufficiently large number in release mode.

If the map was not empty when the overflow happens, the library will invoke self.grow(0) and start infinite probing. This allows an attacker who controls the argument to reserve() to cause a potential denial of service (DoS).

The flaw was corrected in 0.1.20 release of http crate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25574
- https://github.com/hyperium/http/issues/352
- https://github.com/hyperium/http
- https://rustsec.org/advisories/RUSTSEC-2019-0033.html
