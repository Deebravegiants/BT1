# [M] Observable Response Discrepancy in Flask-AppBuilder

## Summary
Severity: Medium
Advisory: GHSA-434h-p4gx-jm89
CVE: CVE-2021-29621
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-05-27
Source: https://github.com/advisories/GHSA-434h-p4gx-jm89
Type: github-advisory

## Affected
- PyPI: `Flask-AppBuilder` — affected >=0 <3.3.0

## Details
### Impact
User enumeration in database authentication in Flask-AppBuilder <= 3.2.3. Allows for a non authenticated user to enumerate existing accounts by timing the response time from the server when you are logging in.

### Patches
Upgrade to 3.3.0

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Flask-AppBuilder](https://github.com/dpgaspar/Flask-AppBuilder)

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-434h-p4gx-jm89
- https://nvd.nist.gov/vuln/detail/CVE-2021-29621
- https://github.com/dpgaspar/Flask-AppBuilder/commit/780bd0e8fbf2d36ada52edb769477e0a4edae580
- https://github.com/dpgaspar/Flask-AppBuilder
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-appbuilder/PYSEC-2021-90.yaml
- https://lists.apache.org/thread.html/r466759f377651f0a690475d5a52564d0e786e82c08d5a5730a4f8352%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r466759f377651f0a690475d5a52564d0e786e82c08d5a5730a4f8352@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r5b754118ba4e996adf03863705d34168bffec202da5c6bdc9bf3add5%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r5b754118ba4e996adf03863705d34168bffec202da5c6bdc9bf3add5@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r91067f953906d93aaa1c69fe2b5472754019cc6bd4f1ba81349d62a0%40%3Ccommits.airflow.apache.org%3E
- https://lists.apache.org/thread.html/r91067f953906d93aaa1c69fe2b5472754019cc6bd4f1ba81349d62a0@%3Ccommits.airflow.apache.org%3E
- https://pypi.org/project/Flask-AppBuilder
