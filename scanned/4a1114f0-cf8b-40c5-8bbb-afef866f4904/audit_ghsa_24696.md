# [H] Silverstripe CMS malicious file upload enables script execution

## Summary
Severity: High
Advisory: GHSA-h77w-655f-6j3m
CVE: CVE-2020-9309
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h77w-655f-6j3m
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=0

## Details
Silverstripe CMS through 4.5 can be susceptible to script execution from malicious upload contents under allowed file extensions (for example HTML code in a TXT file). When these files are stored as protected or draft files, the MIME detection can cause browsers to execute the file contents. Uploads stored as protected or draft files are allowed by default for authorised users only, but can also be enabled through custom logic as well as modules such as silverstripe/userforms. Sites using the previously optional silverstripe/mimevalidator module can configure MIME whitelists rather than extension whitelists, and hence prevent this issue. Sites on the Common Web Platform (CWP) use this module by default, and are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9309
- https://github.com/silverstripe/silverstripe-cms
- https://www.silverstripe.org/download/security-releases/CVE-2020-9309
