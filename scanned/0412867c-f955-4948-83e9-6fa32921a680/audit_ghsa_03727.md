# [M] Plone Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-xvwv-6wvx-px9x
CVE: CVE-2017-1000484
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-xvwv-6wvx-px9x
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.5 <4.3.16
- PyPI: `Plone` — affected >=5.0.0 <5.1.0

## Details
By linking to a specific url in Plone 2.5-5.1rc1 with a parameter, an attacker could send you to his own website. On its own this is not so bad: the attacker could more easily link directly to his own website instead. But in combination with another attack, you could be sent to the Plone login form and login, then get redirected to the specific url, and then get a second redirect to the attacker website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000484
- https://github.com/plone/Products.CMFPlone/issues/2232
- https://github.com/advisories/GHSA-xvwv-6wvx-px9x
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2018-73.yaml
- https://plone.org/security/hotfix/20171128/an-open-redirection-when-calling-a-specific-url
