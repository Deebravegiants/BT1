# [C] Sandbox bypass in fenom

## Summary
Severity: Critical
Advisory: GHSA-674v-3g2w-84gx
CVE: CVE-2021-46433
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-29
Source: https://github.com/advisories/GHSA-674v-3g2w-84gx
Type: github-advisory

## Affected
- Packagist: `fenom/fenom` — affected >=0

## Details
In fenom 2.12.1 and before, there is a way in fenom/src/Fenom/Template.php function getTemplateCode()to bypass sandbox to execute arbitrary PHP code when disable_native_funcs is true.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46433
- https://github.com/fenom-template/fenom/issues/331
- https://github.com/fenom-template/fenom
