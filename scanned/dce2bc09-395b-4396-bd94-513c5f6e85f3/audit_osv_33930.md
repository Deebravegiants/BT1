# [M] EspoCRM is vulnerable to access denial through double slash in URI corrupting router cache

## Summary
Severity: Medium
Advisory: CVE-2025-52892
Aliases: GHSA-26x2-6wch-j8pf
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-52892
Type: osv

## Details
EspoCRM is a web application with a frontend designed as a single-page application and a REST API backend written in PHP. In versions 9.1.6 and below, if a user loads Espo in the browser with double slashes (e.g https://domain//#Admin) and the webserver does not strip the double slash, it can cause a corrupted Slim router's cache. This will make the instance unusable until there is a completed rebuild. This is fixed in version 9.1.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52892.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-26x2-6wch-j8pf
- https://nvd.nist.gov/vuln/detail/CVE-2025-52892
- https://github.com/espocrm/espocrm/commit/929611f317ce8892ea75873b0ab3094c0c510ff3
