# [M] iana-time-zone vulnerable to use after free in MacOS / iOS implementation

## Summary
Severity: Medium
Advisory: GHSA-3fg9-hcq5-vxrc
CWE: CWE-416
Ecosystem: crates.io
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-3fg9-hcq5-vxrc
Type: github-advisory

## Affected
- crates.io: `iana-time-zone` — affected >=0.1.43 <0.1.45

## Details
In iana-time-zone v0.1.43 a use-after-free bug in the MacOS / iOS implementation was introduced.

The copied system time zone was released before its name was copied.
If the system time zone was changed between the call of `CFRelease` and `str::to_owned()`,
random memory would be copied.

## References
- https://github.com/strawlab/iana-time-zone/pull/54
- https://github.com/strawlab/iana-time-zone
- https://rustsec.org/advisories/RUSTSEC-2022-0049.html
