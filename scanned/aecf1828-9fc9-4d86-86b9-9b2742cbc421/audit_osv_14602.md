# [M] CVE-2019-1023

## Summary
Severity: Medium
Advisory: CVE-2019-1023
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-06-12
Source: https://osv.dev/vulnerability/CVE-2019-1023
Type: osv

## Details
An information disclosure vulnerability exists when the scripting engine does not properly handle objects in memory in Microsoft Edge. An attacker who successfully exploited the vulnerability could obtain information to further compromise the user’s system.
In a web-based attack scenario, an attacker could host a website in an attempt to exploit the vulnerability. In addition, compromised websites and websites that accept or host user-provided content could contain specially crafted content that could exploit the vulnerability. However, in all cases an attacker would have no way to force a user to view the attacker-controlled content. Instead, an attacker would have to convince a user to take action. For example, an attacker could trick a user into clicking a link that takes the user to the attacker's site.
The security update addresses the vulnerability by changing how the scripting engine handles objects in memory.

## References
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-1023
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1023
