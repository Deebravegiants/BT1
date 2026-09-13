# [M] SAML XML Signature wrapping in PySAML2

## Summary
Severity: Medium
Advisory: GHSA-f4g9-h89h-jgv9
CVE: CVE-2021-21238
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-01-21
Source: https://github.com/advisories/GHSA-f4g9-h89h-jgv9
Type: github-advisory

## Affected
- PyPI: `pysaml2` — affected >=0 <6.5.0

## Details
### Impact

All users of pysaml2 that use the default `CryptoBackendXmlSec1` backend and need to verify signed SAML documents are impacted. `pysaml2 <= 6.4.1` does not validate the SAML document against an XML schema. This allows invalid XML documents to trick the verification process, by presenting elements with a valid signature inside elements whose content has been malformed. The verification is offloaded to `xmlsec1` and `xmlsec1` will not validate every signature in the given document, but only the first it finds in the given scope.

### Patches

Users should upgrade to pysaml2 `v6.5.0`.

### Workarounds

No workaround provided at this point.

### References

No references provided at this point.

### Credits

- Victor Schönfelder Garcia (isits AG International School of IT Security)
- Juraj Somorovsky (Paderborn University)
- Vladislav Mladenov (Ruhr University Bochum)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [pysaml2](https://github.com/IdentityPython/pysaml2)
* Email us at [the incident-response address](mailto:incident-response@idpy.org)

## References
- https://github.com/IdentityPython/pysaml2/security/advisories/GHSA-f4g9-h89h-jgv9
- https://nvd.nist.gov/vuln/detail/CVE-2021-21238
- https://github.com/IdentityPython/pysaml2/commit/1d8fd268f5bf887480a403a7a5ef8f048157cc14
- https://github.com/IdentityPython/pysaml2
- https://github.com/IdentityPython/pysaml2/releases/tag/v6.5.0
- https://github.com/pypa/advisory-database/tree/main/vulns/pysaml2/PYSEC-2021-48.yaml
- https://pypi.org/project/pysaml2
