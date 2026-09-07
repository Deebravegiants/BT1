# [M] GetmeUK ContentTools Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-4f2v-2gpq-qhjg
CVE: CVE-2025-2699
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-4f2v-2gpq-qhjg
Type: github-advisory

## Affected
- npm: `ContentTools` — affected >=0

## Details
A vulnerability was found in GetmeUK ContentTools up to 1.6.16. It has been rated as problematic. Affected by this issue is some unknown functionality of the component Image Handler. The manipulation of the argument onload leads to cross site scripting. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2699
- https://gist.github.com/Masamuneee/657f2e2b0eb5bf9b0d4dbb79f00dac37
- https://github.com/GetmeUK/ContentTools
- https://vuldb.com/?ctiid.300716
- https://vuldb.com/?id.300716
- https://vuldb.com/?submit.515864
