# [C] Improper Input Validation in renderdoc

## Summary
Severity: Critical
Advisory: GHSA-vhfr-v4w9-45v8
CVE: CVE-2019-16142
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vhfr-v4w9-45v8
Type: github-advisory

## Affected
- crates.io: `renderdoc` — affected >=0 <0.5.0

## Details
Affected versions of this crate exposed several methods which took self by immutable reference, despite the requesting the RenderDoc API to set a mutable value internally. This is technically unsound and calling these methods from multiple threads without synchronization could lead to unexpected and unpredictable behavior. The flaw was corrected in release 0.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16142
- https://github.com/ebkalderon/renderdoc-rs/pull/32
- https://github.com/ebkalderon/renderdoc-rs
- https://rustsec.org/advisories/RUSTSEC-2019-0018.html
