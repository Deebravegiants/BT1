# [M] DOMPurify Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8hgg-xxm5-3873
CVE: CVE-2019-25155
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-8hgg-xxm5-3873
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <1.0.11

## Details
DOMPurify before 1.0.11 allows reverse tabnabbing in demos/hooks-target-blank-demo.html because links lack a 'rel="noopener noreferrer"' attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25155
- https://github.com/cure53/DOMPurify/pull/337
- https://github.com/cure53/DOMPurify/commit/7601c33a57e029cce51d910eda5179a3f1b51c83
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/compare/1.0.10...1.0.11
