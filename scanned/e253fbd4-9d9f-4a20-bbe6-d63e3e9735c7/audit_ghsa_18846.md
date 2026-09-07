# [M] Mammoth is vulnerable to Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-rmjr-87wv-gf87
CVE: CVE-2025-11849
CWE: CWE-22
Ecosystem: Maven, NuGet, PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:H (CVSS_V3)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-rmjr-87wv-gf87
Type: github-advisory

## Affected
- npm: `mammoth` — affected >=0.3.25 <1.11.0
- Maven: `org.zwobble.mammoth:mammoth` — affected >=0 <1.11.0
- PyPI: `mammoth` — affected >=0.3.25 <1.11.0
- NuGet: `Mammoth` — affected >=0 <1.11.0

## Details
Versions of the package mammoth from 0.3.25 and before 1.11.0; versions of the package mammoth from 0.3.25 and before 1.11.0; versions of the package mammoth before 1.11.0; versions of the package org.zwobble.mammoth:mammoth before 1.11.0 are vulnerable to Directory Traversal due to the lack of path or file type validation when processing a docx file containing an image with an external link (r:link attribute instead of embedded r:embed). The library resolves the URI to a file path and after reading, the content is encoded as base64 and included in the HTML output as a data URI. An attacker can read arbitrary files on the system where the conversion is performed or cause an excessive resources consumption by crafting a docx file that links to special device files such as /dev/random or /dev/zero.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11849
- https://github.com/mwilliamson/mammoth.js/commit/c54aaeb43a7941317c1f3c119ffa92090f988820
- https://gist.github.com/AudunWA/4d690d9ae5efdafe7cf71d9c2ee90a10
- https://github.com/mwilliamson/java-mammoth
- https://security.snyk.io/vuln/SNYK-DOTNET-MAMMOTH-13561968
- https://security.snyk.io/vuln/SNYK-JAVA-ORGZWOBBLEMAMMOTH-13561969
- https://security.snyk.io/vuln/SNYK-JS-MAMMOTH-13554470
- https://security.snyk.io/vuln/SNYK-PYTHON-MAMMOTH-13561967
