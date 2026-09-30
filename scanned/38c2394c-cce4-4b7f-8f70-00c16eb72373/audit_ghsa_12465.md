# [M] Always incorrect control flow in github.com/mojocn/base64Captcha

## Summary
Severity: Medium
Advisory: GHSA-5mmw-p5qv-w3x5
CVE: CVE-2023-45292
CWE: CWE-345, CWE-670
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-5mmw-p5qv-w3x5
Type: github-advisory

## Affected
- Go: `github.com/mojocn/base64Captcha` — affected >=0 <1.3.6

## Details
When using the default implementation of Verify to check a Captcha, verification can be bypassed. For example, if the first parameter is a non-existent id, the second parameter is an empty string, and the third parameter is true, the function will always consider the Captcha to be correct.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45292
- https://github.com/mojocn/base64Captcha/issues/120
- https://github.com/mojocn/base64Captcha/commit/5ab86bd6f333aad3936f912fc52b411168dcd4a7
- https://github.com/mojocn/base64Captcha/commit/9b11012caca58925f1e47c770f79f2fa47e3ad13
- https://github.com/mojocn/base64Captcha
- https://pkg.go.dev/vuln/GO-2023-2386
