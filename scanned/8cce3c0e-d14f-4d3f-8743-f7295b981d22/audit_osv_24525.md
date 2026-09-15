# [M] PoDoFo PdfXRefStreamParserObject.cpp readXRefStreamEntry heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2023-2241
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-04-22
Source: https://osv.dev/vulnerability/CVE-2023-2241
Type: osv

## Details
A vulnerability, which was classified as critical, was found in PoDoFo 0.10.0. Affected is the function readXRefStreamEntry of the file PdfXRefStreamParserObject.cpp. The manipulation leads to heap-based buffer overflow. An attack has to be approached locally. The exploit has been disclosed to the public and may be used. The patch is identified as 535a786f124b739e3c857529cecc29e4eeb79778. It is recommended to apply a patch to fix this issue. VDB-227226 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2241.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2241
- https://vuldb.com/?id.227226
- https://github.com/podofo/podofo/issues/69
- https://vuldb.com/?ctiid.227226
- https://github.com/podofo/podofo/commit/535a786f124b739e3c857529cecc29e4eeb79778
- https://github.com/podofo/podofo/files/11260976/poc-file.zip
