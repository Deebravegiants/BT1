# [M] Cross-site Scripting in invenio-communities

## Summary
Severity: Medium
Advisory: GHSA-mfv8-q39f-mgfg
CVE: CVE-2019-1020005
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-mfv8-q39f-mgfg
Type: github-advisory

## Affected
- PyPI: `invenio-communities` — affected >=0 <1.0.0a20

## Details
## Cross-Site Scripting (XSS) vulnerability in Jinja templates

### Impact
A Cross-Site Scripting (XSS) vulnerability was discovered in two Jinja templates in the Invenio-Communities module. The vulnerability allows a user to create a new community and include script element tags inside the description and page fields. 

### Patches
The problem has been patched in v1.0.0a20.

### For more information
If you have any questions or comments about this advisory:
* Email us at [info@inveniosoftware.org](mailto:info@inveniosoftware.org)

## References
- https://github.com/inveniosoftware/invenio-communities/security/advisories/GHSA-mfv8-q39f-mgfg
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020005
- https://github.com/inveniosoftware/invenio-communities/commit/505da72c5acd7dfbd4148f884c73c9c3372b76f4
- https://github.com/advisories/GHSA-mfv8-q39f-mgfg
- https://github.com/pypa/advisory-database/tree/main/vulns/invenio-communities/PYSEC-2019-25.yaml
