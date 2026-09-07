# [M] django-photologue vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-287q-jfcp-9vhv
CVE: CVE-2022-4526
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-287q-jfcp-9vhv
Type: github-advisory

## Affected
- PyPI: `django-photologue` — affected >=0 <3.16

## Details
A vulnerability was found in django-photologue up to 3.15.1 and classified as problematic. Affected by this issue is some unknown functionality of the file photologue/templates/photologue/photo_detail.html of the component Default Template Handler. The manipulation of the argument object.caption leads to cross site scripting. The attack may be launched remotely. Upgrading to version 3.16 is able to address this issue. The name of the patch is 960cb060ce5e2964e6d716ff787c72fc18a371e7. It is recommended to apply a patch to fix this issue. VDB-215906 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4526
- https://github.com/richardbarran/django-photologue/issues/223
- https://github.com/richardbarran/django-photologue/commit/960cb060ce5e2964e6d716ff787c72fc18a371e7
- https://github.com/pypa/advisory-database/tree/main/vulns/django-photologue/PYSEC-2022-43061.yaml
- https://github.com/richardbarran/django-photologue
- https://vuldb.com/?id.215906
