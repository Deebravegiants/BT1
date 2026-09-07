# [C] mpp has multiple payment bypass and griefing vulnerabilities

## Summary
Severity: Critical
Advisory: GHSA-fxc9-7j2w-vx54
CWE: CWE-288, CWE-294, CWE-345
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-fxc9-7j2w-vx54
Type: github-advisory

## Affected
- crates.io: `mpp` — affected >=0 <0.8.0

## Details
### Impact
Multiple vulnerabilities were discovered which allowed for undesirable behaviors, including:
- Performing free `tempo/charge` requests
- Replaying existing `tempo/charge` requests
- Performing free `tempo/session` requests
- Piggybacking off existing `tempo/session` channels
- Griefing existing `tempo/session` channels
- Manipulate the fee payer of a `tempo/charge` or `tempo/session` handler into paying for requests
- Replaying existing `stripe/charge` requests

### Patches
The issues are patched in 0.8.0

### Workarounds
There are no workarounds available for these vulnerabilities

## References
- https://github.com/tempoxyz/mpp-rs/security/advisories/GHSA-fxc9-7j2w-vx54
- https://github.com/tempoxyz/mpp-rs
- https://github.com/tempoxyz/mpp-rs/releases/tag/v0.8.0
