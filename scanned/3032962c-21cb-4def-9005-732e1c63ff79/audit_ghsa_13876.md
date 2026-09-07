# [M] generator-hottowel Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f8hv-rx9p-f9r4
CVE: CVE-2016-15025
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-20
Source: https://github.com/advisories/GHSA-f8hv-rx9p-f9r4
Type: github-advisory

## Affected
- npm: `generator-hottowel` — affected >=0 <0.5.0

## Details
A vulnerability, which was classified as problematic, was found in generator-hottowel 0.0.11. Affected is an unknown function of the file app/templates/src/server/_app.js of the component 404 Error Handler. The manipulation leads to cross site scripting. It is possible to launch the attack remotely. The name of the patch is c17092fd4103143a9ddab93c8983ace8bf174396. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-221484.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15025
- https://github.com/johnpapa/generator-hottowel/pull/174
- https://github.com/johnpapa/generator-hottowel/commit/c17092fd4103143a9ddab93c8983ace8bf174396
- https://github.com/johnpapa/generator-hottowel
- https://vuldb.com/?ctiid.221484
- https://vuldb.com/?id.221484
