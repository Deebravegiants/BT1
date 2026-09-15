# [H] Eta vulnerable to Code Injection via templates rendered with user-defined data

## Summary
Severity: High
Advisory: GHSA-mf6x-hrgr-658f
CVE: CVE-2022-25967
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-30
Source: https://github.com/advisories/GHSA-mf6x-hrgr-658f
Type: github-advisory

## Affected
- npm: `eta` — affected >=0 <2.0.0

## Details
Versions of the package eta before 2.0.0 are vulnerable to Remote Code Execution (RCE) by overwriting template engine configuration variables with view options received from The Express render API. **Note:** This is exploitable only for users who are rendering templates with user-defined data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25967
- https://github.com/eta-dev/eta/commit/5651392462ee0ff19d77c8481081a99e5b9138dd
- https://github.com/eta-dev/eta
- https://github.com/eta-dev/eta/blob/9c8e4263d3a559444a3881a85c1607bf344d0b28/src/compile-string.ts%23L21
- https://github.com/eta-dev/eta/blob/9c8e4263d3a559444a3881a85c1607bf344d0b28/src/file-handlers.ts%23L182
- https://security.snyk.io/vuln/SNYK-JS-ETA-2936803
