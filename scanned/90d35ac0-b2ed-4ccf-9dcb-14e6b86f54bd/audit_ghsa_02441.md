# [M] Remote Code Execution via unsafe classes in otherwise permitted modules

## Summary
Severity: Medium
Advisory: GHSA-qcx9-j53g-ccgf
CVE: CVE-2021-32807
CWE: CWE-1321, CWE-915
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-05
Source: https://github.com/advisories/GHSA-qcx9-j53g-ccgf
Type: github-advisory

## Affected
- PyPI: `AccessControl` — affected >=4.0 <4.3
- PyPI: `AccessControl` — affected >=5.0 <5.2
- PyPI: `zope` — affected >=4.0 <4.3
- PyPI: `zope` — affected >=5.0 <5.2

## Details
### Impact
The module `AccessControl` defines security policies for Python code used in restricted code within Zope applications. Restricted code is any code that resides in Zope's object database, such as the contents of `Script (Python)` objects. 

The policies defined in `AccessControl` severely restrict access to Python modules and only exempt a few that are deemed safe, such as Python's `string` module. However, full access to the `string` module also allows access to the class `Formatter`, which can be overridden and extended within `Script (Python)` in a way that provides access to other unsafe Python libraries. Those unsafe Python libraries can be used for remote code execution.

By default, you need to have the admin-level Zope "Manager" role to add or edit `Script (Python)` objects through the web. Only sites that allow untrusted users to add/edit these scripts through the web - which would be a very unusual configuration to begin with - are at risk.

### Patches
The problem has been fixed in AccessControl 4.3 and 5.2.
Only AccessControl versions 4 and 5 are vulnerable, and only on Python 3, not Python 2.7.

### Workarounds
A site administrator can restrict adding/editing `Script (Python)` objects through the web using the standard Zope user/role permission mechanisms. Untrusted users should not be assigned the Zope Manager role and adding/editing these scripts through the web should be restricted to trusted users only. This is the default configuration in Zope.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [AccessControl issue tracker](https://github.com/zopefoundation/AccessControl/issues)
* Email us at [security@plone.org](mailto:security@plone.org)

## References
- https://github.com/zopefoundation/AccessControl/security/advisories/GHSA-qcx9-j53g-ccgf
- https://github.com/zopefoundation/Zope/security/advisories/GHSA-g4gq-j4p2-j8fr
- https://nvd.nist.gov/vuln/detail/CVE-2021-32807
- https://github.com/zopefoundation/AccessControl/commit/ae2dab0cc34e6dd1561c5b12d4a56cd140f87e1d
- https://github.com/zopefoundation/AccessControl/commit/b42dd4badf803bb9fb71ac34cd9cb0c249262f2c
- https://github.com/zopefoundation/Zope/commit/869f947e586517566509e0ccdd4d99b60704cc02
- https://github.com/zopefoundation/Zope/commit/f72a18dda8e9bf2aedb46168761668464a4be988
- https://github.com/pypa/advisory-database/tree/main/vulns/accesscontrol/PYSEC-2021-335.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/accesscontrol/PYSEC-2021-370.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2021-368.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2021-875.yaml
- https://github.com/zopefoundation/AccessControl
- https://github.com/zopefoundation/AccessControl/blob/master/CHANGES.rst#51-2021-07-30
