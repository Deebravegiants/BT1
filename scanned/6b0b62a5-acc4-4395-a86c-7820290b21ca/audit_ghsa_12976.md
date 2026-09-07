# [M] Badaso vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-7422-7rq6-j4qv
CVE: CVE-2023-38970
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-31
Source: https://github.com/advisories/GHSA-7422-7rq6-j4qv
Type: github-advisory

## Affected
- Packagist: `uasoft-indonesia/badaso` — affected >=0

## Details
Cross Site Scripting vulnerabiltiy in Badaso v.0.0.1 thru v.2.9.7 allows a remote attacker to execute arbitrary code via a crafted payload to the Name of member parameter in the add new member function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38970
- https://github.com/anh91/uasoft-indonesia--badaso/blob/main/XSS3.md
- https://github.com/uasoft-indonesia/badaso
- https://panda002.hashnode.dev/badaso-version-297-has-an-xss-vulnerability-in-new-member
