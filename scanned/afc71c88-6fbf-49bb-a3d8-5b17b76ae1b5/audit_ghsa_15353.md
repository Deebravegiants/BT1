# [H] Flowise Unauthenticated Denial of Service (DoS) vulnerability

## Summary
Severity: High
Advisory: GHSA-48x4-mx8f-gr4h
CVE: CVE-2024-8182
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-48x4-mx8f-gr4h
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
An Unauthenticated Denial of Service (DoS) vulnerability exists in Flowise version 1.8.2 leading to a complete crash of the instance running a vulnerable version due to improper handling of user supplied input to the `/api/v1/get-upload-file` api endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8182
- https://github.com/FlowiseAI/Flowise
- https://tenable.com/security/research/tra-2024-34
