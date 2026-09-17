# [H] Plone Open Redirection vulnerability via next parameter

## Summary
Severity: High
Advisory: GHSA-56p3-rrp4-2j82
CVE: CVE-2013-4200
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-56p3-rrp4-2j82
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.1 <4.1.1
- PyPI: `Plone` — affected >=4.2 <4.2.6
- PyPI: `Plone` — affected >=4.3 <4.3.2

## Details
The isURLInPortal method in the URLTool class in in_portal.py in Plone 2.1 through 4.1, 4.2.x through 4.2.5, and 4.3.x through 4.3.1 treats URLs starting with a space as a relative URL, which allows remote attackers to bypass the allow_external_login_sites filtering property,  redirect users to arbitrary web sites, and conduct phishing attacks via a space before a URL in the "next" parameter to acl_users/credentials_cookie_auth/require_login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4200
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-4200
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2014-64.yaml
- http://plone.org/products/plone-hotfix/releases/20130618
- http://plone.org/products/plone/security/advisories/20130618-announcement
- http://www.openwall.com/lists/oss-security/2013/08/01/2
