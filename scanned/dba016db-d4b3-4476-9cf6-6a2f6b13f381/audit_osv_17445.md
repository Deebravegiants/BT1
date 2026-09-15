# [C] CVE-2020-15181

## Summary
Severity: Critical
Advisory: CVE-2020-15181
Aliases: GHSA-xrc8-fjp4-h4fv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-18
Source: https://osv.dev/vulnerability/CVE-2020-15181
Type: osv

## Details
The Alfresco Reset Password add-on before version 1.2.0 relies on untrusted inputs in a security decision. Intruders can get admin's access to the system using the vulnerability in the project. Impacts all servers where this add-on is installed. The problem is fixed in version 1.2.0

## References
- https://github.com/FlexSolution/AlfrescoResetPassword/security/advisories/GHSA-xrc8-fjp4-h4fv
- https://github.com/FlexSolution/AlfrescoResetPassword/commit/5927b9651356c4cd952cb9b485292583d305b47c
