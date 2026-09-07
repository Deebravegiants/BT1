# [M] Cross-site Scripting in pegasus/google-for-jobs

## Summary
Severity: Medium
Advisory: GHSA-hfm8-2q22-h7hv
CVE: CVE-2021-43561
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-hfm8-2q22-h7hv
Type: github-advisory

## Affected
- Packagist: `pegasus/google-for-jobs` — affected >=0 <1.5.1
- Packagist: `pegasus/google-for-jobs` — affected >=2.0.0 <2.1.1

## Details
An XSS issue was discovered in the google_for_jobs (aka Google for Jobs) extension before 1.5.1 and 2.x before 2.1.1 for TYPO3. The extension fails to properly encode user input for output in HTML context. A TYPO3 backend user account is required to exploit the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43561
- https://github.com/pegasuswerbeagentur/google_for_jobs
- https://typo3.org/security/advisory/typo3-ext-sa-2021-015
