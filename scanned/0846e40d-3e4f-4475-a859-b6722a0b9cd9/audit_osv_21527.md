# [C] CVE-2021-43779

## Summary
Severity: Critical
Advisory: CVE-2021-43779
Aliases: GHSA-q5fp-xpr8-77jh
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-01-05
Source: https://osv.dev/vulnerability/CVE-2021-43779
Type: osv

## Details
GLPI is an open source IT Asset Management, issue tracking system and service desk system. The GLPI addressing plugin in versions < 2.9.1 suffers from authenticated Remote Code Execution vulnerability, allowing access to the server's underlying operating system using command injection abuse of functionality. There is no workaround for this issue and users are advised to upgrade or to disable the addressing plugin.

## References
- https://github.com/hansmach1ne/CVE-portfolio/tree/main/CVE-2021-43779
- https://github.com/pluginsGLPI/addressing/commit/6f55964803054a5acb5feda92c7c7f1d91ab5366
- https://github.com/hansmach1ne/MyExploits/tree/main/RCE_GLPI_addressing_plugin
- https://github.com/pluginsGLPI/addressing/security/advisories/GHSA-q5fp-xpr8-77jh
