# [H] OWSLib vulnerable to XML External Entity (XXE) Injection

## Summary
Severity: High
Advisory: GHSA-8h9c-r582-mggc
CVE: CVE-2023-27476
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-8h9c-r582-mggc
Type: github-advisory

## Affected
- PyPI: `OWSLib` — affected >=0 <0.28.1

## Details
### Impact

OWSLib's XML parser (which supports both `lxml` and `xml.etree`) does not disable entity resolution for `lxml`, and could lead to arbitrary file reads from an attacker-controlled XML payload. This affects all XML parsing in the codebase.

### Patches

- Use only lxml for XML handling, adding `resolve_entities=False` to `lxml`'s parser: https://github.com/geopython/OWSLib/pull/863

### Workarounds

```python
patch_well_known_namespaces(etree)
etree.set_default_parser(
    parser=etree.XMLParser(resolve_entities=False)
)
```

### References

- [`GHSL-2022-131`](https://securitylab.github.com/advisories/GHSL-2022-131_OWSLib/)

## References
- https://github.com/geopython/OWSLib/security/advisories/GHSA-8h9c-r582-mggc
- https://nvd.nist.gov/vuln/detail/CVE-2023-27476
- https://github.com/geopython/OWSLib/pull/863
- https://github.com/geopython/OWSLib/pull/863/commits/b92687702be9576c0681bb11cad21eb631b9122f
- https://github.com/geopython/OWSLib
- https://github.com/geopython/OWSLib/releases/tag/0.28.1
- https://github.com/pypa/advisory-database/tree/main/vulns/owslib/PYSEC-2023-86.yaml
- https://lists.debian.org/debian-lts-announce/2023/06/msg00032.html
- https://securitylab.github.com/advisories/GHSL-2022-131_owslib
- https://www.debian.org/security/2023/dsa-5426
