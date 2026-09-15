# [C] FreeRTOS-Plus-TCP Buffer Over-Read in DNS Response Parser

## Summary
Severity: Critical
Advisory: CVE-2024-38373
Aliases: GHSA-ppcp-rg65-58mv
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-38373
Type: osv

## Details
FreeRTOS-Plus-TCP is a lightweight TCP/IP stack for FreeRTOS. FreeRTOS-Plus-TCP versions 4.0.0 through 4.1.0 contain a buffer over-read issue in the DNS Response Parser when parsing domain names in a DNS response. A carefully crafted DNS response with domain name length value greater than the actual domain name length, could cause the parser to read beyond the DNS response buffer. This issue affects applications using DNS functionality of the FreeRTOS-Plus-TCP stack. Applications that do not use DNS functionality are not affected, even when the DNS functionality is enabled. This vulnerability has been patched in version 4.1.1.

## References
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/releases/tag/V4.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38373.json
- https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/security/advisories/GHSA-ppcp-rg65-58mv
- https://nvd.nist.gov/vuln/detail/CVE-2024-38373
