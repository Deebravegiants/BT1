# [M] RefindPlusRepo RefindPlus BootLog.c GetDebugLogFile null pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2025-4002
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-28
Source: https://osv.dev/vulnerability/CVE-2025-4002
Type: osv

## Details
A vulnerability was found in RefindPlusRepo RefindPlus 0.14.2.AB and classified as problematic. Affected by this issue is the function GetDebugLogFile of the file Library/MemLogLib/BootLog.c. The manipulation leads to null pointer dereference. Attacking locally is a requirement. The patch is identified as d2143a1e2deefddd9b105fb7160763c4f8d47ea2. It is recommended to apply a patch to fix this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4002.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4002
- https://vuldb.com/?id.306338
- https://vuldb.com/?submit.558122
- https://github.com/RefindPlusRepo/RefindPlus/issues/204
- https://github.com/RefindPlusRepo/RefindPlus/issues/204#issuecomment-2696817643
- https://vuldb.com/?ctiid.306338
- https://github.com/RefindPlusRepo/RefindPlus/commit/d2143a1e2deefddd9b105fb7160763c4f8d47ea2
