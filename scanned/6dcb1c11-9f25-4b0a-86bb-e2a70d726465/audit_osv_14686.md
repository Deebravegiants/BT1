# [C] CVE-2019-10759

## Summary
Severity: Critical
Advisory: CVE-2019-10759
Aliases: GHSA-r3x4-wr4h-pw33
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-10-15
Source: https://osv.dev/vulnerability/CVE-2019-10759
Type: osv

## Details
safer-eval before 1.3.4 are vulnerable to Arbitrary Code Execution. A payload using constructor properties can escape the sandbox and execute arbitrary code.

## References
- https://snyk.io/vuln/SNYK-JS-SAFEREVAL-173772
