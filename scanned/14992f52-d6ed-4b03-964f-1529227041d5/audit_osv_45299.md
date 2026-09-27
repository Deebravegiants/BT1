# [H] libcurl's ASN1 parser has this utf8asn1str() function used for parsing an ASN.1 UTF-8 string

## Summary
Severity: High
Advisory: JLSEC-2025-36
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-36
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.6.0+0 <8.9.0+0
- Julia: `LibCURL_jll` — affected >=8.6.0+0 <8.9.0+0

## Details
libcurl's ASN1 parser has this utf8asn1str() function used for parsing an ASN.1 UTF-8 string. Itcan detect an invalid field and return error. Unfortunately, when doing so it also invokes `free()` on a 4 byte localstack buffer.  Most modern malloc implementations detect this error and immediately abort. Some however accept the input pointer and add that memory to its list of available chunks. This leads to the overwriting of nearby stack memory. The content of the overwrite is decided by the `free()` implementation; likely to be memory pointers and a set of flags.  The most likely outcome of exploting this flaw is a crash, although it cannot be ruled out that more serious results can be had in special circumstances.

## References
- http://www.openwall.com/lists/oss-security/2024/07/24/1
- http://www.openwall.com/lists/oss-security/2024/07/24/5
- https://curl.se/docs/CVE-2024-6197.html
- https://curl.se/docs/CVE-2024-6197.json
- https://hackerone.com/reports/2559516
- https://security.netapp.com/advisory/ntap-20241129-0008/
