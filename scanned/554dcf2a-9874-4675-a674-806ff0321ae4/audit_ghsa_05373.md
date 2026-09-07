# [H] seroval Affected by Remote Code Execution via JSON Deserialization

## Summary
Severity: High
Advisory: GHSA-3rxj-6cgf-8cfw
CVE: CVE-2026-23737
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-3rxj-6cgf-8cfw
Type: github-advisory

## Affected
- npm: `seroval` — affected >=0 <1.4.1

## Details
Improper input handling in the JSON deserialization component can lead to arbitrary JavaScript code execution.

The vulnerability can be exploited via overriding constant value and error deserialization, which allows indirect access to unsafe JS evaluation. This requires at least the ability to perform 4 separate requests on the same function and partial knowledge of how the serialized data is used during later runtime processing. 

This vulnerability affects the `fromJSON` and `fromCrossJSON` functions in a client-to-server transmission scenario.

No known workarounds or mitigations are known, so please upgrade to the patched version.

## References
- https://github.com/lxsmnsyc/seroval/security/advisories/GHSA-3rxj-6cgf-8cfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-23737
- https://github.com/lxsmnsyc/seroval/commit/ce9408ebc87312fcad345a73c172212f2a798060
- https://github.com/lxsmnsyc/seroval
