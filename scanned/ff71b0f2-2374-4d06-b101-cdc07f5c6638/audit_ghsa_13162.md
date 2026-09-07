# [M] plone.rest vulnerable to Denial of Service when ++api++ is used many times

## Summary
Severity: Medium
Advisory: GHSA-h6rp-mprm-xgcq
CVE: CVE-2023-42457
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-h6rp-mprm-xgcq
Type: github-advisory

## Affected
- PyPI: `plone.rest` — affected >=2.0.0a1 <2.0.1
- PyPI: `plone.rest` — affected >=3.0.0 <3.0.1

## Details
### Impact
When the `++api++` traverser is accidentally used multiple times in a url, handling it takes increasingly longer, making the server less responsive.

### Patches
Patches will be released in `plone.rest` 2.0.1 and 3.0.1.  Series 1.x is not affected.

### Workarounds
In your frontend web server (nginx, Apache) you can redirect `/++api++/++api++` to `/++api++`.

## References
- https://github.com/plone/plone.rest/security/advisories/GHSA-h6rp-mprm-xgcq
- https://nvd.nist.gov/vuln/detail/CVE-2023-42457
- https://github.com/plone/plone.rest/commit/43b4a7e86206e237e1de5ca3817ed071575882f7
- https://github.com/plone/plone.rest/commit/77846a9842889b24f35e8bedc2e9d461388d3302
- https://github.com/plone/plone.rest
- https://github.com/pypa/advisory-database/tree/main/vulns/plone-rest/PYSEC-2023-178.yaml
- http://www.openwall.com/lists/oss-security/2023/09/22/2
