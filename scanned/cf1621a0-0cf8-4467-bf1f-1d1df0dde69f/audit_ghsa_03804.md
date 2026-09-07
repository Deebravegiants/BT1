# [M] Cross-site scripting invenio-records

## Summary
Severity: Medium
Advisory: GHSA-vxh3-mvv7-265j
CVE: CVE-2019-1020003
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-vxh3-mvv7-265j
Type: github-advisory

## Affected
- PyPI: `invenio-records` — affected >=0 <1.0.2
- PyPI: `invenio-records` — affected >=1.1.0 <1.1.1
- PyPI: `invenio-records` — affected >=1.2.0 <1.2.2

## Details
## Cross-Site Scripting (XSS) vulnerability in administration interface

### Impact
A Cross-Site Scripting (XSS) vulnerability was discovered when rendering JSON for a record in the administration interface. The vulnerability could be exploited by e.g. a user who had access to upload a new record, that an admin user would then later view in the admin interface.

### Patches
All supported versions of Invenio-Records have been patched. You should upgrade to either v1.0.1, v1.1.1 or v1.2.2

### For more information
If you have any questions or comments about this advisory:
* Email us at [info@inveniosoftware.org](mailto:info@inveniosoftware.org)

## References
- https://github.com/inveniosoftware/invenio-records/security/advisories/GHSA-vxh3-mvv7-265j
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020003
- https://github.com/advisories/GHSA-vxh3-mvv7-265j
- https://github.com/pypa/advisory-database/tree/main/vulns/invenio-records/PYSEC-2019-27.yaml
