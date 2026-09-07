# [H] Remote Code Execution via Script (Python) objects under Python 3

## Summary
Severity: High
Advisory: GHSA-g4gq-j4p2-j8fr
CVE: CVE-2021-32811
CWE: CWE-1321, CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-05
Source: https://github.com/advisories/GHSA-g4gq-j4p2-j8fr
Type: github-advisory

## Affected
- PyPI: `Zope` — affected >=4.0 <4.6.3
- PyPI: `Zope` — affected >=5.0 <5.3

## Details
### Impact
Background: The optional add-on package `Products.PythonScripts` adds `Script (Python)` to the list of content items a user can add to the Zope object database. Inside these scripts users can write Python code that is executed when rendered through the web. The code environment in these script objects is limited, it relies on the `RestrictedPython` package to provide a "safe" subset of Python instructions as well as the `AccessControl` package that defines security policies for execution in the context of a Zope application.

Recently the `AccessControl` package was updated to fix a remote code execution security issue. A link to the security advisory is provided in the References section below. The bug tightens the `AccessControl` security policies for Zope by blocking access to unsafe classes inside the Python `string` module.

You are only affected if the following are true:

- You use Python 3 for your Zope deployment (Zope 4 on Python 2 is not affected)
- You run Zope 4 below version 4.6.3 or Zope 5 below version 5.3
- You have installed the optional `Products.PythonScripts` add-on package

By default, you need to have the admin-level Zope "Manager" role to add or edit Script (Python) objects through the web. Only sites that allow untrusted users to add/edit these scripts through the web - which would be a very unusual configuration to begin with - are at risk.

### Patches
The problem has been fixed in `AccessControl` versions 4.3 and 5.2. Zope releases 4.6.3 and 5.3 now require these new `AccessControl` releases.

### Workarounds
A site administrator can restrict adding/editing Script (Python) objects through the web using the standard Zope user/role permission mechanisms. Untrusted users should not be assigned the Zope Manager role and adding/editing these scripts through the web should be restricted to trusted users only. This is the default configuration in Zope.

### References
* [AccessControl security advisory GHSA-qcx9-j53g-ccgf](https://github.com/zopefoundation/AccessControl/security/advisories/GHSA-qcx9-j53g-ccgf)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [Zope issue tracker](https://github.com/zopefoundation/Zope/issues)
* Email us at [security@plone.org](mailto:security@plone.org)

## References
- https://github.com/zopefoundation/AccessControl/security/advisories/GHSA-qcx9-j53g-ccgf
- https://github.com/zopefoundation/Zope/security/advisories/GHSA-g4gq-j4p2-j8fr
- https://nvd.nist.gov/vuln/detail/CVE-2021-32811
- https://github.com/zopefoundation/Zope/commit/869f947e586517566509e0ccdd4d99b60704cc02
- https://github.com/zopefoundation/Zope/commit/f72a18dda8e9bf2aedb46168761668464a4be988
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2021-368.yaml
- https://github.com/zopefoundation/Zope
