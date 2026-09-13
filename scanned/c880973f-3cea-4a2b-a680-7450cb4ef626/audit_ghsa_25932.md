# [C] Code injection in RazorEngine

## Summary
Severity: Critical
Advisory: GHSA-ph3v-2hq5-5qfq
CVE: CVE-2021-46703
CWE: CWE-1336
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-07
Source: https://github.com/advisories/GHSA-ph3v-2hq5-5qfq
Type: github-advisory

## Affected
- NuGet: `RazorEngine` — affected >=0

## Details
In the IsolatedRazorEngine component of Antaris RazorEngine through 4.5.1-alpha001, an attacker can execute arbitrary .NET code in a sandboxed environment (if users can externally control template contents). NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46703
- https://github.com/Antaris/RazorEngine/issues/585
- https://github.com/Antaris/RazorEngine
