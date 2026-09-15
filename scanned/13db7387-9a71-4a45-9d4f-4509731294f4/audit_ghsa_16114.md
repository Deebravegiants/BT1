# [M] ReDoS in giskard's transformation.py (GHSL-2024-324)

## Summary
Severity: Medium
Advisory: GHSA-pjwm-cr36-mwv3
CVE: CVE-2024-52524
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:Clear (CVSS_V4)
Published: 2024-11-14
Source: https://github.com/advisories/GHSA-pjwm-cr36-mwv3
Type: github-advisory

## Affected
- PyPI: `giskard` — affected >=0 <2.15.5

## Details
# ReDoS in Giskard text perturbation detector

A Remote Code Execution (ReDoS) vulnerability was discovered in Giskard component by the [GitHub Security Lab](https://securitylab.github.com) team. When processing datasets with specific text patterns with Giskard detectors, this vulnerability could trigger exponential regex evaluation times, potentially leading to denial of service.

## Details

The vulnerability affects Giskard's punctuation removal transformation used in the text perturbation detection. A regex used to detect URLs and links was vulnerable to catastrophic backtracking that could be triggered by specific patterns in the text.

## Affected version

Giskard versions prior to 2.15.5 are affected. Users should upgrade to version 2.15.5 or later, which includes a fix for this vulnerability.

## Impact

This vulnerability can cause extended computation times or crashes in Giskard when processing text containing certain patterns.

## Credit

This issue was discovered and reported by GHSL team member [@kevinbackhouse (Kevin Backhouse)](https://github.com/kevinbackhouse).

## References
- https://github.com/Giskard-AI/giskard/security/advisories/GHSA-pjwm-cr36-mwv3
- https://nvd.nist.gov/vuln/detail/CVE-2024-52524
- https://github.com/Giskard-AI/giskard/commit/48ce81f5c626171767188d6f0669498fb613b4d3
- https://github.com/Giskard-AI/giskard
