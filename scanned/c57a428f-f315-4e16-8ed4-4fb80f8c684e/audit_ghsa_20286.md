# [C] Delegate functions are missing `Send` bound

## Summary
Severity: Critical
Advisory: GHSA-x4mq-m75f-mx8m
CWE: CWE-820
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-x4mq-m75f-mx8m
Type: github-advisory

## Affected
- crates.io: `windows` — affected >=0.1.2 <0.32.0

## Details
Affected versions of this crate did not require event handlers to have `Send` bound despite there being no guarantee of them being called on any particular thread, which can potentially lead to data races and undefined behavior.

The flaw was corrected in commit [afe3252](https://github.com/microsoft/windows-rs/commit/afe32525c22209aa8f632a0f4ad607863b51796a) by adding `Send` bounds.

## References
- https://github.com/microsoft/windows-rs/issues/1409
- https://github.com/microsoft/windows-rs/commit/afe32525c22209aa8f632a0f4ad607863b51796a
- https://github.com/microsoft/windows-rs
- https://rustsec.org/advisories/RUSTSEC-2022-0008.html
