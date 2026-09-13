# [M] CVE-2020-1065

## Summary
Severity: Medium
Advisory: CVE-2020-1065
Aliases: GHSA-9hjg-j983-mqcc
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-1065
Type: osv

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory. The vulnerability could corrupt memory in such a way that an attacker could execute arbitrary code in the context of the current user. An attacker who successfully exploited the vulnerability could gain the same user rights as the current user.
If the current user is logged on with administrative user rights, an attacker who successfully exploited the vulnerability could take control of an affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights.
The security update addresses the vulnerability by modifying how the ChakraCore scripting engine handles objects in memory.

## References
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2020-1065
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1065
