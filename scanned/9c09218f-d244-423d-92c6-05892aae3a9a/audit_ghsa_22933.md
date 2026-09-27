# [M] Gleez CMS Vulnerability Allows Forced Browsing to Profile Page of Other Users

## Summary
Severity: Medium
Advisory: GHSA-hh92-wg7v-8vfr
CVE: CVE-2018-16704
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hh92-wg7v-8vfr
Type: github-advisory

## Affected
- Packagist: `gleez/cms` — affected >=0

## Details
An issue was discovered in Gleez CMS v1.2.0. Because of an Insecure Direct Object Reference vulnerability, it is possible for attackers (logged in users) to view profile page of other users, as demonstrated by navigating to `user/3` on `demo.gleezcms.org`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16704
- https://github.com/gleez/cms/issues/801
- https://github.com/gleez/cms
