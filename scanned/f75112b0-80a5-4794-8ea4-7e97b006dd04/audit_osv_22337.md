# [C] Remote Code Injection

## Summary
Severity: Critical
Advisory: CVE-2022-25759
Aliases: GHSA-5gxc-fxcr-9326
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H/E:P)
Published: 2022-07-22
Source: https://osv.dev/vulnerability/CVE-2022-25759
Type: osv

## Details
The package convert-svg-core before 0.6.2 are vulnerable to Remote Code Injection via sending an SVG file containing the payload.

## References
- https://security.snyk.io/vuln/SNYK-JS-CONVERTSVGCORE-2849633
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25759.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-25759
- https://github.com/neocotic/convert-svg/issues/81
- https://github.com/neocotic/convert-svg/commit/7e6031ac7427cf82cf312cb4a25040f2e6efe7a5
- https://github.com/neocotic/convert-svg/pull/82
