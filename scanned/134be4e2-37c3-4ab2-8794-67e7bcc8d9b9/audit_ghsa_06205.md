# [H] Weblate has IDOR in GroupViewSet that allows authenticated project manager to gain unauthorized read access to any private project

## Summary
Severity: High
Advisory: GHSA-2q2q-jr9g-v9rf
CVE: CVE-2026-55228
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-2q2q-jr9g-v9rf
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <2026.7

## Details
### Impact
The API did not properly handle project- and workspace-scoped teams and allowed setting invalid configurations, including granting access to projects the user has no access to.

### Patches
* https://github.com/WeblateOrg/weblate/pull/19970


### References

Parts of this issue were independently reported by four reporters:
 * @H3xV0rT3x via GitHub
 * [imhego](https://hackerone.com/imhego) via HackerOne
 * [v01demort](https://hackerone.com/v01demort) via HackerOne
 * [b4nder](https://hackerone.com/b4nder) via HackerOne

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-2q2q-jr9g-v9rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55228
- https://github.com/WeblateOrg/weblate/pull/19970
- https://github.com/WeblateOrg/weblate/commit/19babc99b05f2cc299b5090f90f79d8181f25d79
- https://github.com/WeblateOrg/weblate
