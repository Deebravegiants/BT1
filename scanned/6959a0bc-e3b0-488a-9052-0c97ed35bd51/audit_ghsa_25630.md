# [H] Improper Removal of Sensitive Information Before Storage or Transfer in irrd

## Summary
Severity: High
Advisory: GHSA-cqxx-66wh-8pjw
CVE: CVE-2022-24798
CWE: CWE-212
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-cqxx-66wh-8pjw
Type: github-advisory

## Affected
- PyPI: `irrd` — affected >=4.2.0 <4.2.3

## Details
IRRd did not always filter password hashes in query responses relating to `mntner` objects and database exports. This may have allowed adversaries to retrieve some of these hashes, perform a brute-force search for the clear-text passphrase, and use these to make unauthorised changes to affected IRR objects. This issue only affected instances that process password hashes, which means it is limited to IRRd instances that serve authoritative databases. IRRd instances operating solely as mirrors of other IRR databases are not affected.

The issue occurred:
* For `mntner` objects where all password hash names (`MD5-PW` and `CRYPT-PW`) were in lower or mixed case in the `auth` attribute. For these objects, hashes remained in the output of all queries of any method and all database exports made with the `export_destination` setting. Fortunately, objects in the common public IRR database virtually all use uppercase hash names which means very few of those objects were affected.
* For any GraphQL queries that queried the `auth` field on `mntner` objects.
* For any GraphQL queries that queried the `objectText` field on the `journal` field on `mntner` objects, if the `nrtm_access_list` setting permitted journal access.

The two GraphQL cases are visible in logs, allowing users to determine whether any existing objects had their hashes exposed.
This has been fixed in IRRd 4.2.3 and the main branch. Versions in the 4.1.x series never were affected. Users of the 4.2.x series are strongly recommended to upgrade. All users running a more recent version from the main branch should update to the latest version. Alternatively, but not recommended, apply the patch manually [for 4.2.x]

## References
- https://github.com/irrdnet/irrd/security/advisories/GHSA-cqxx-66wh-8pjw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24798
- https://github.com/irrdnet/irrd/commit/0e41bae8d3d27316381a2fc7b466597230e35ec6
- https://github.com/irrdnet/irrd/commit/fdffaf8dd71713f06e99dff417e6aa1e6fa84b70
- https://github.com/irrdnet/irrd
- https://github.com/pypa/advisory-database/tree/main/vulns/irrd/PYSEC-2022-178.yaml
- https://irrd.readthedocs.io/en/stable/releases/4.2.3
