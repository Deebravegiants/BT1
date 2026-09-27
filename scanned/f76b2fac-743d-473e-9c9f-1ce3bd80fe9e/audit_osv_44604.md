# [M] Heap over-read or silent misparse via 32-bit truncation of JSON length in BSON JSON parser

## Summary
Severity: Medium
Advisory: CVE-2026-84970
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-84970
Type: osv

## Details
A numeric truncation weakness exists in the JSON parsing component of the MongoDB C++ Driver's BSON library. An actor who controls the text that an embedding application hands to the library's public JSON parsing interface, when that text is very large, can cause the library to read memory beyond the supplied buffer and return it to the caller, to silently accept only part of the input as a complete document, or to terminate the process. No MongoDB server, credentials, or non-default configuration is required; the effect is confined to the process that uses the library.

## References
- https://jira.mongodb.org/browse/CXX-3547
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84970.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84970
