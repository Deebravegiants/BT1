# [H] thorsten/phpmyfaq vulnerable to business logic errors

## Summary
Severity: High
Advisory: GHSA-gx43-fqrx-6fcw
CVE: CVE-2023-1887
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-gx43-fqrx-6fcw
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.1.12

## Details
thorsten/phpmyfaq prior to 3.1.12 allows users with edit-only permissions to add and delete categories and add FAQs. This has been fixed in 3.1.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1887
- https://github.com/thorsten/phpmyfaq/commit/400d9cd988d3287515c56b2ad6343026966f1a89
- https://github.com/thorsten/phpMyFAQ
- https://huntr.dev/bounties/e4a58835-96b5-412c-a17e-3ceed30231e1
