# [C] CVE-2023-49208

## Summary
Severity: Critical
Advisory: CVE-2023-49208
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-23
Source: https://osv.dev/vulnerability/CVE-2023-49208
Type: osv

## Details
scheme/webauthn.c in Glewlwyd SSO server before 2.7.6 has a possible buffer overflow during FIDO2 credentials validation in webauthn registration.

## References
- https://github.com/babelouest/glewlwyd/releases/tag/v2.7.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49208.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49208
- https://github.com/babelouest/glewlwyd/commit/f9d8c06aae8dfe17e761b18b577ff169e059e812
