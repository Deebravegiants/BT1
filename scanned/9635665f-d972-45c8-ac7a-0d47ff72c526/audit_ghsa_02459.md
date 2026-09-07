# [H] URL Redirection to Untrusted Site ('Open Redirect') in Products.isurlinportal

## Summary
Severity: High
Advisory: GHSA-q3m9-9fj2-mfwr
CVE: CVE-2021-32806
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-05
Source: https://github.com/advisories/GHSA-q3m9-9fj2-mfwr
Type: github-advisory

## Affected
- PyPI: `Products.isurlinportal` — affected >=0 <1.2.0

## Details
### Impact
Various parts of Plone use the 'is url in portal' check for security, mostly to see if it is safe to redirect to a url. A url like `https://example.org` is not in the portal.
But the url `https:example.org` without slashes tricks our code and it _is_ considered to be in the portal.
When redirecting, some browsers go to `https://example.org`, others give an error.
Attackers may use this to redirect you to their site, especially as part of a phishing attack.

### Patches
The problem has been patched in `Products.isurlinportal` 1.2.0.
This is a recommended upgrade for all users of Plone 4.3 and 5, on Python 2.7 or higher.
It has not been tested on earlier Plone or Python versions.
Upcoming Plone 5.2.5 and higher will include the new version.

### Discovered
This vulnerability was discovered and reported by Yuji Tounai of Mitsui Bussan Secure Directions, Inc. Thank you!

### For more information
If you have any questions or comments about this advisory:
* Email the Plone Security Team at [security@plone.org](mailto:security@plone.org), especially when you think you have discovered a security problem or when you are not sure.
* Open an issue in [the tracker](https://github.com/plone/Products.isurlinportal/issues) if your question or comment can be public.

## References
- https://github.com/plone/Products.isurlinportal/security/advisories/GHSA-q3m9-9fj2-mfwr
- https://nvd.nist.gov/vuln/detail/CVE-2021-32806
- https://github.com/plone/Products.isurlinportal/commit/d4fd34990d18adf05a10dc5e2bb4b066798280ba
- https://github.com/plone/Products.isurlinportal
- https://github.com/pypa/advisory-database/tree/main/vulns/products-isurlinportal/PYSEC-2021-323.yaml
- http://jvn.jp/en/jp/JVN50804280/index.html
