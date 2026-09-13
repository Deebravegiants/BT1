# [M] CVE-2026-26825

## Summary
Severity: Medium
Advisory: CVE-2026-26825
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-26825
Type: osv

## Details
A use-of-uninitialized memory vulnerability exists in libxls 1.6.3 when parsing malformed XLS files. The issue is reachable via xls_parseWorkBook() and is triggered by uninitialized heap memory originating from the OLE layer (ole2_read). The flaw is detectable with MemorySanitizer (MSAN) and can lead to undefined behavior, incorrect parsing logic, or potential information disclosure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26825.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26825
- https://github.com/libxls/libxls/issues/156
