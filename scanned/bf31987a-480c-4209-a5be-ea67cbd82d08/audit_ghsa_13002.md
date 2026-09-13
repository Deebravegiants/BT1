# [C] Cockpit PHP Remote File Inclusion vulnerability

## Summary
Severity: Critical
Advisory: GHSA-xcq3-7pf3-5jvc
CVE: CVE-2023-4195
CWE: CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2023-08-06
Source: https://github.com/advisories/GHSA-xcq3-7pf3-5jvc
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.6.3

## Details
PHP Remote File Inclusion in GitHub repository cockpit-hq/cockpit prior to 2.6.3. Users may upload php files through the system file upload utility to obtain remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4195
- https://github.com/cockpit-hq/cockpit/commit/800c05f1984db291769ffa5fdfb1d3e50968e95b
- https://github.com/cockpit-hq/cockpit
- https://huntr.dev/bounties/0bd5da2f-0e29-47ce-90f3-06518656bfd6
