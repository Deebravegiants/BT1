# [M] Open Redirect in AllTube

## Summary
Severity: Medium
Advisory: GHSA-jmhf-9fj8-88gh
CVE: CVE-2022-0692
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-23
Source: https://github.com/advisories/GHSA-jmhf-9fj8-88gh
Type: github-advisory

## Affected
- Packagist: `rudloff/alltube` — affected >=0 <3.0.1

## Details
### Impact
Releases prior to 3.0.1 are vulnerable to an open redirect vulnerability that allows an attacker to construct a URL that redirects to an arbitrary external domain.

### Patches
3.0.1 contains a fix for this vulnerability.
(The 1.x and 2.x releases are not maintained anymore.)

### References
* https://github.com/rudloff/alltube/commit/bc14b6e45c766c05757fb607ef8d444cbbfba71a
* https://huntr.dev/bounties/4fb39400-e08b-47af-8c1f-5093c9a51203/
* https://nvd.nist.gov/vuln/detail/CVE-2022-0692

## References
- https://github.com/Rudloff/alltube/security/advisories/GHSA-jmhf-9fj8-88gh
- https://nvd.nist.gov/vuln/detail/CVE-2022-0692
- https://github.com/rudloff/alltube/commit/bc14b6e45c766c05757fb607ef8d444cbbfba71a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/rudloff/alltube/CVE-2022-0692.yaml
- https://github.com/Rudloff/alltube
- https://huntr.dev/bounties/4fb39400-e08b-47af-8c1f-5093c9a51203
