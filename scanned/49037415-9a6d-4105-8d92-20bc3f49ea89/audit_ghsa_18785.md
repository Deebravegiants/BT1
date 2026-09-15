# [H] pdfmake is vulnerable to Throttling via repeatedly redirecting URL in file embedding

## Summary
Severity: High
Advisory: GHSA-rj3r-r7hh-jxfq
CVE: CVE-2025-11362
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-rj3r-r7hh-jxfq
Type: github-advisory

## Affected
- npm: `pdfmake` — affected >=0.3.0-beta.1 <0.3.0-beta.17

## Details
Versions of the package pdfmake from 0.3.0-beta.1 to before 0.3.0-beta.17 are vulnerable to Allocation of Resources Without Limits or Throttling via repeatedly redirect URL in file embedding. An attacker can cause the application to crash or become unresponsive by providing crafted input that triggers this condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11362
- https://github.com/bpampuch/pdfmake/issues/2886
- https://github.com/bpampuch/pdfmake/commit/741169634bf07730e010cd77477b6cc038e846ed
- https://github.com/bpampuch/pdfmake
- https://security.snyk.io/vuln/SNYK-JS-PDFMAKE-10223297
