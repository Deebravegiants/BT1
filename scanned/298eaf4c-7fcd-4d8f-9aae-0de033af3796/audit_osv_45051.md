# [M] PYSEC-2023-193

## Summary
Severity: Medium
Advisory: PYSEC-2023-193
Aliases: CVE-2023-44389, GHSA-m755-gxxg-r5qh
Ecosystem: PyPI
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/PYSEC-2023-193
Type: osv

## Affected
- PyPI: `zope` — affected >=0 <21dfa78609ffd8b6bd8143805678ebbacae5141a, >=4.0 <4.8.11

## Details
Zope is an open-source web application server. The title property, available on most Zope objects, can be used to store script code that is executed while viewing the affected object in the Zope Management Interface (ZMI). All versions of Zope 4 and Zope 5 are affected. Patches will be released with Zope versions 4.8.11 and 5.8.6

## References
- https://github.com/zopefoundation/Zope/security/advisories/GHSA-m755-gxxg-r5qh
- https://github.com/zopefoundation/Zope/commit/aeaf2cdc80dff60815e3706af448f086ddc3b98d
- https://github.com/zopefoundation/Zope/commit/21dfa78609ffd8b6bd8143805678ebbacae5141a
