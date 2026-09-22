# [C] aXMLRPC XML External Entity vulnerability

## Summary
Severity: Critical
Advisory: GHSA-g4r8-28fp-f255
CVE: CVE-2020-36641
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-g4r8-28fp-f255
Type: github-advisory

## Affected
- Maven: `fr.turri:aXMLRPC` — affected >=0 <1.12.1

## Details
A vulnerability classified as problematic was found in gturri aXMLRPC up to 1.12.0. This vulnerability affects the function `ResponseParser` of the file `src/main/java/de/timroes/axmlrpc/ResponseParser.java`. The manipulation leads to xml external entity reference. Upgrading to version 1.12.1 is able to address this issue. The name of the patch is ad6615b3ec41353e614f6ea5fdd5b046442a832b. It is recommended to upgrade the affected component. VDB-217450 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36641
- https://github.com/gturri/aXMLRPC/commit/456752ebc1ef4c0db980cb5b01a0b3cd0a9e0bae
- https://github.com/gturri/aXMLRPC/commit/ad6615b3ec41353e614f6ea5fdd5b046442a832b
- https://github.com/gturri/aXMLRPC
- https://github.com/gturri/aXMLRPC/releases/tag/aXMLRPC-1.12.1
- https://github.com/gturri/aXMLRPC/releases/tag/aXMLRPC-1.14.0
- https://vuldb.com/?ctiid.217450
- https://vuldb.com/?id.217450
