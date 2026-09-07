# [H] Remote Code Execution via traversal in TAL expressions

## Summary
Severity: High
Advisory: GHSA-5pr9-v234-jw36
CVE: CVE-2021-32633
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-5pr9-v234-jw36
Type: github-advisory

## Affected
- PyPI: `Zope` — affected >=0 <4.6
- PyPI: `Zope` — affected >=5.0 <5.2

## Details
### Impact
Most Python modules are not available for using in TAL expressions that you can add through-the-web, for example in Zope Page Templates. This restriction avoids file system access, for example via the 'os' module. But some of the untrusted modules are available indirectly through Python modules that are available for direct use.

By default, you need to have the Manager role to add or edit Zope Page Templates through the web. Only sites that allow untrusted users to add/edit Zope Page Templates through the web are at risk.

### Patches
The problem has been fixed in Zope 5.2 and 4.6.

### Workarounds
A site administrator can restrict adding/editing Zope Page Templates through the web using the standard Zope user/role permission mechanisms. Untrusted users should not be assigned the Zope Manager role and adding/editing Zope Page Templates through the web should be restricted to trusted users only.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [Zope issue tracker](https://github.com/zopefoundation/Zope/issues)
* Email us at [security@plone.org](mailto:security@plone.org)

## References
- https://github.com/zopefoundation/Zope/security/advisories/GHSA-5pr9-v234-jw36
- https://nvd.nist.gov/vuln/detail/CVE-2021-32633
- https://github.com/zopefoundation/Zope/commit/1f8456bf1f908ea46012537d52bd7e752a532c91
- https://cyllective.com/blog/post/plone-authenticated-rce-cve-2021-32633
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2021-88.yaml
- https://github.com/zopefoundation/Zope
- http://www.openwall.com/lists/oss-security/2021/05/21/1
- http://www.openwall.com/lists/oss-security/2021/05/22/1
