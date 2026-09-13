# [H] CVE-2019-6964

## Summary
Severity: High
Advisory: CVE-2019-6964
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-6964
Type: osv

## Details
A heap-based buffer over-read in Service_SetParamStringValue in cosa_x_cisco_com_ddns_dml.c of the RDK RDKB-20181217-1 CcspPandM module may allow attackers with login credentials to achieve information disclosure and code execution by crafting an AJAX call responsible for DDNS configuration with an exactly 64-byte username, password, or domain, for which the buffer size is insufficient for the final '\0' character. This is related to the CcspCommonLibrary and WebUI modules.

## References
- https://dojo.bullguard.com/dojo-by-bullguard/blog/the-gateway-is-wide-open
