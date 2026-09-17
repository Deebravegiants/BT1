# [C] move_elements can double-free objects on panic

## Summary
Severity: Critical
Advisory: GHSA-3qm2-rfqw-fmrw
CVE: CVE-2021-28031
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3qm2-rfqw-fmrw
Type: github-advisory

## Affected
- crates.io: `scratchpad` — affected >=0 <1.3.1

## Details
Affected versions of scratchpad used ptr::read to read elements while calling a user provided function f on them. Since the pointer read duplicates ownership, a panic inside the user provided f function could cause a double free when unwinding.

The flaw was fixed in commit `891561bea` by removing the unsafe block and using a plain iterator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28031
- https://github.com/okready/scratchpad/issues/1
- https://github.com/okready/scratchpad/commit/891561bea
- https://github.com/okready/scratchpad
- https://rustsec.org/advisories/RUSTSEC-2021-0030.html
