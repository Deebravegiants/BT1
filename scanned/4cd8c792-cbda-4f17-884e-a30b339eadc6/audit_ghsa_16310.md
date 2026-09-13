# [M] Showdown vulnerable to Regular Expression Denial of Service (ReDoS) in link/anchor parsing

## Summary
Severity: Medium
Advisory: GHSA-rmmh-p597-ppvv
CVE: CVE-2024-1899
CWE: CWE-674, CWE-777
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-26
Source: https://github.com/advisories/GHSA-rmmh-p597-ppvv
Type: github-advisory

## Affected
- npm: `showdown` — affected >=0

## Details
Showdownjs, versions <= 2.1.0, `anchors` subparser used to parse links has a nested regular expression which can lead to denial of service conditions given malicious input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1899
- https://github.com/showdownjs/showdown
- https://www.tenable.com/security/research/tra-2024-05
