# [H] akbr patch-into was discovered to contain a prototype pollution via the function patchInto

## Summary
Severity: High
Advisory: GHSA-gh4x-qv3p-m9pm
CVE: CVE-2024-38991
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-gh4x-qv3p-m9pm
Type: github-advisory

## Affected
- npm: `@akbr/patch-into` — affected 1.0.1

## Details
akbr patch-into version 1.0.1 was discovered to contain a prototype pollution via the function patchInto. This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38991
- https://gist.github.com/mestrtee/8851413e3b33a96f191f0e9c81706532
- github.com/akbr/patch-into
