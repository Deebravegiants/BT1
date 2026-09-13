# [C] GeniXCMS Arbitrary User Password Reset Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wm7g-rmgg-9837
CVE: CVE-2017-8827
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wm7g-rmgg-9837
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected >=0 <1.1.2

## Details
forgotpassword.php in GeniXCMS lacks a rate limit, which might allow remote attackers to cause a denial of service (login inability) or possibly conduct Arbitrary User Password Reset attacks via a series of requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8827
- https://github.com/semplon/GeniXCMS/issues/75
- https://github.com/semplon/GeniXCMS/commit/f7b4a8278cdcf29ecf7f1eaa1b9f088d505ca61a
- https://github.com/GeniXCMS/GeniXCMS
