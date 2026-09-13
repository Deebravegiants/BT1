# [M] CVE-2019-0993

## Summary
Severity: Medium
Advisory: CVE-2019-0993
Aliases: GHSA-2rfj-2mwp-787v
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2019-06-12
Source: https://osv.dev/vulnerability/CVE-2019-0993
Type: osv

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge (HTML-based). The vulnerability could corrupt memory in such a way that an attacker could execute arbitrary code in the context of the current user. An attacker who successfully exploited the vulnerability could gain the same user rights as the current user. If the current user is logged on with administrative user rights, an attacker who successfully exploited the vulnerability could take control of an affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights.
In a web-based attack scenario, an attacker could host a specially crafted website that is designed to exploit the vulnerability through Microsoft Edge (HTML-based) and then convince a user to view the website. The attacker could also take advantage of compromised websites and websites that accept or host user-provided content or advertisements. These websites could contain specially crafted content that could exploit the vulnerability.
The security update addresses the vulnerability by modifying how the Chakra scripting engine handles objects in memory.

## References
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-0993
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0993
