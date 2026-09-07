# [H] Double free in glsl-layout

## Summary
Severity: High
Advisory: GHSA-cx4j-fxr7-jxg8
CVE: CVE-2021-25902
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cx4j-fxr7-jxg8
Type: github-advisory

## Affected
- crates.io: `glsl-layout` — affected >=0 <0.4.0

## Details
Affected versions of this crate did not guard against panic within the user-provided function f (2nd parameter of fn map_array), and thus panic within f causes double drop of a single object.

The flaw was corrected in the 0.4.0 release by wrapping the object vulnerable to a double drop within ManuallyDrop<T>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25902
- https://github.com/rustgd/glsl-layout/pull/10
- https://github.com/rustgd/glsl-layout
- https://rustsec.org/advisories/RUSTSEC-2021-0005.html
