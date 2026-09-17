# [H] Xibo CMS API has SQL Injection via DataSet Filter Parameter

## Summary
Severity: High
Advisory: CVE-2026-31952
Aliases: GHSA-rq92-f6fv-3629
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31952
Type: osv

## Details
Xibo is an open source digital signage platform with a web content management system and Windows display player software. Versions 1.7 through 4.4.0 have an SQL injection vulnerability in the API routes inside the CMS responsible for Filtering DataSets. This allows an authenticated user to to obtain and modify arbitrary data from the Xibo database by injecting specially crafted values in to the API filter parameter. Exploitation of the vulnerability is possible on behalf of an authorized user who has either of the `Access to DataSet Feature` privilege or the `Access to the Layout Feature` privilege. Users should upgrade to version 4.4.1 which fixes this issue. Customers who host their CMS with Xibo Signage have been patched if they are using 4.4, 4.3, 3.3, 2.3 or 1.8. Upgrading to a fixed version is necessary to remediate. Patches are available for earlier versions of Xibo CMS that are out of support, namely 3.3, 2.3, and 1.8.

## References
- https://github.com/xibosignage/xibo-cms/releases/tag/4.4.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31952.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-rq92-f6fv-3629
- https://nvd.nist.gov/vuln/detail/CVE-2026-31952
- https://github.com/dasgarner/xibo-cms/commit/b8d25fe6cb0232b645c3850afdc2499b0e46c1e6
- https://github.com/xibosignage/xibo-cms/commit/87e0a26b0c06e349561a6becdc00f3bb01259736
- https://github.com/xibosignage/xibo-cms/commit/ed213cb4f42d4f50cf8012e01e95bb70127fc6a4
