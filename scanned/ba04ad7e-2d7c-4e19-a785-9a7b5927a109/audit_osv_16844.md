# [H] CVE-2020-0604

## Summary
Severity: High
Advisory: CVE-2020-0604
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-17
Source: https://osv.dev/vulnerability/CVE-2020-0604
Type: osv

## Details
A remote code execution vulnerability exists in Visual Studio Code when it process environment variables after opening a project. An attacker who successfully exploited the vulnerability could run arbitrary code in the context of the current user. If the current user is logged on with administrative user rights, an attacker could take control of the affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights.
To exploit this vulnerability, an attacker would need to convince a target to clone a repository and open it in Visual Studio Code. Attacker-specified code would execute when the target opened the integrated terminal.
The update address the vulnerability by modifying the way Visual Studio Code handles environment variables.

## References
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0604
