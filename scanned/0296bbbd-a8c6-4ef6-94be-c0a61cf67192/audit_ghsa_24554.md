# [M] GeniXCMS denial of service (account blockage)

## Summary
Severity: Medium
Advisory: GHSA-2m9r-pm7q-wr6f
CVE: CVE-2017-14231
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2m9r-pm7q-wr6f
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected >=0 <1.1.0

## Details
GeniXCMS before 1.1.0 allows remote attackers to cause a denial of service (account blockage) by leveraging the mishandling of certain username substring relationships, such as the admin<script> username versus the admin username, related to register.php, User.class.php, and Type.class.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14231
- https://github.com/semplon/GeniXCMS/issues/78
- https://github.com/semplon/GeniXCMS/commit/e0ad60b2bb967fa3f63c35b92afe84c5f3b31009
- https://github.com/GeniXCMS/GeniXCMS
- https://github.com/semplon/GeniXCMS/releases/tag/v1.1.0
