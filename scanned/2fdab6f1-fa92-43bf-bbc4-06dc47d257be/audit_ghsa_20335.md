# [M] Stored XSS via HTML fields in SilverStripe Framework

## Summary
Severity: Medium
Advisory: GHSA-jx34-gqqq-r6gm
CVE: CVE-2022-25238
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-jx34-gqqq-r6gm
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.10.9

## Details
SilverStripe Framework through 4.10.8 allows XSS, inside of script tags that can can be added to website content via XHR by an authenticated CMS user if the cwp-core module is not installed on the sanitise_server_side contig is not set to true in project code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25238
- https://docs.silverstripe.org/en/4/changelogs/4.10.1
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2022-25238.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-25238
