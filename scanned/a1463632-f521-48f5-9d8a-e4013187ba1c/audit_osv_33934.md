# [M] Tuleap vulnerable to user enumeration via the lost password form

## Summary
Severity: Medium
Advisory: CVE-2025-52899
Aliases: GHSA-xqf3-xxxf-x3c2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-07-29
Source: https://osv.dev/vulnerability/CVE-2025-52899
Type: osv

## Details
Tuleap is an Open Source Suite created to facilitate management of software development and collaboration. In Tuleap Community Edition prior to version 16.9.99.1750843170 and Tuleap Enterprise Edition prior to 16.8-4 and 16.9-2, the forgot password form allows for user enumeration. This is fixed in Tuleap Community Edition version 16.9.99.1750843170 and Tuleap Enterprise Edition 16.8-4 and 16.9-2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52899.json
- https://github.com/Enalean/tuleap/commit/5c72d6d253016d38ed472eb7918f772d074ddb07
- https://github.com/Enalean/tuleap/security/advisories/GHSA-xqf3-xxxf-x3c2
- https://nvd.nist.gov/vuln/detail/CVE-2025-52899
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=5c72d6d253016d38ed472eb7918f772d074ddb07
- https://tuleap.net/plugins/tracker/?aid=43674
