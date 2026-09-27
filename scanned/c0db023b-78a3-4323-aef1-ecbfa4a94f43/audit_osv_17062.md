# [M] CVE-2020-1180

## Summary
Severity: Medium
Advisory: CVE-2020-1180
Aliases: GHSA-wc43-7wj6-4ggr
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2020-1180
Type: osv

## Details
<p>A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory. The vulnerability could corrupt memory in such a way that an attacker could execute arbitrary code in the context of the current user. An attacker who successfully exploited the vulnerability could gain the same user rights as the current user.</p>
<p>If the current user is logged on with administrative user rights, an attacker who successfully exploited the vulnerability could take control of an affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights.</p>
<p>The security update addresses the vulnerability by modifying how the ChakraCore scripting engine handles objects in memory.</p>

## References
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1180
