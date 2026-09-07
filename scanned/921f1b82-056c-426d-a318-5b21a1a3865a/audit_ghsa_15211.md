# [H] Nginx-UI vulnerable to authenticated RCE through injecting into the application config via CRLF

## Summary
Severity: High
Advisory: GHSA-qcjq-7f7v-pvc8
CVE: CVE-2024-23828
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-29
Source: https://github.com/advisories/GHSA-qcjq-7f7v-pvc8
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0 <1.9.10-0.20240126104956-d70e37c8575e

## Details
### Summary

Fix bypass to the following bugs

- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-pxmr-q2x3-9x9m
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-8r25-68wm-jw35

Allowing to inject directly in the `app.ini` via CRLF to change the value of `test_config_cmd` and `start_cmd` resulting in an Authenticated RCE

### Impact
Authenticated Remote execution on the host

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-qcjq-7f7v-pvc8
- https://nvd.nist.gov/vuln/detail/CVE-2024-23828
- https://github.com/0xJacky/nginx-ui/commit/d70e37c8575e25b3da7203ff06da5e16c77a42d1
- https://github.com/0xJacky/nginx-ui
- https://pkg.go.dev/vuln/GO-2024-2480
