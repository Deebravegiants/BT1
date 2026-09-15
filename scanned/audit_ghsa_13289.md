# [H] Products.CMFCore unauthenticated denial of service and crash via unchecked use of input with Python's marshal module

## Summary
Severity: High
Advisory: GHSA-4hpj-8rhv-9x87
CVE: CVE-2023-36814
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-4hpj-8rhv-9x87
Type: github-advisory

## Affected
- PyPI: `Products.CMFCore` — affected >=3.0 <3.2
- PyPI: `Products.CMFCore` — affected >=0 <2.7.1

## Details
### Impact
The use of Python's marshal module to handle unchecked input in a public method on `PortalFolder` objects can lead to an unauthenticated denial of service and crash situation. The code in question is exposed by all portal software built on top of `Products.CMFCore`, such as Plone. All deployments are vulnerable.

### Patches
The code has been fixed in `Products.CMFCore` version 3.2.

### Workarounds
Users can make the affected `decodeFolderFilter` method unreachable by editing the `PortalFolder.py` module in `Products.CMFCore` by hand and then restarting Zope. Go to line 233 of `PortalFolder.py` and remove both the `@security.public` decorator for `decodeFolderFilter` as well as the method's entire docstring. This is safe because the method is not actually used by current code.

### References
- Products.CMFCore security advisory [GHSA-4hpj-8rhv-9x87](https://github.com/zopefoundation/Products.CMFCore/security/advisories/GHSA-4hpj-8rhv-9x87)

### Credits
Thanks go to Nicolas VERDIER from onepoint.

### For more information

If you have any questions or comments about this advisory:

- Open an issue in the [Products.CMFCore issue tracker](https://github.com/zopefoundation/Products.CMFCore/issues)
- Email us at [security@plone.org](mailto:security@plone.org)

## References
- https://github.com/zopefoundation/Products.CMFCore/security/advisories/GHSA-4hpj-8rhv-9x87
- https://nvd.nist.gov/vuln/detail/CVE-2023-36814
- https://github.com/zopefoundation/Products.CMFCore/commit/40f03f43a60f28ca9485c8ef429efef729be54e5
- https://github.com/zopefoundation/Products.CMFCore/commit/c1847a9042abe7965271fa73762dfe091b576de
- https://github.com/pypa/advisory-database/tree/main/vulns/products-cmfcore/PYSEC-2023-113.yaml
- https://github.com/zopefoundation/Products.CMFCore
