# [M] CVE-2020-19007

## Summary
Severity: Medium
Advisory: CVE-2020-19007
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-08-26
Source: https://osv.dev/vulnerability/CVE-2020-19007
Type: osv

## Details
Halo blog 1.2.0 allows users to submit comments on blog posts via /api/content/posts/comments. The javascript code supplied by the attacker will then execute in the victim user's browser.

## References
- https://github.com/halo-dev/halo/issues/547
