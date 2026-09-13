# [H] Audiobookshelf Server-Side Request Forgery and Arbitrary File Read Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-47619
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-47619
Type: osv

## Details
Audiobookshelf is a self-hosted audiobook and podcast server. In versions 2.4.3 and prior, users with the update permission are able to read arbitrary files, delete arbitrary files and send a GET request to arbitrary URLs and read the response. This issue may lead to Information Disclosure. As of time of publication, no patches are available.

## References
- https://github.com/advplyr/audiobookshelf/blob/d7b2476473ef1934eedec41425837cddf2d4b13e/server/controllers/AuthorController.js#L66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47619.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47619
- https://securitylab.github.com/advisories/GHSL-2023-203_GHSL-2023-204_audiobookshelf/
