# [M] CVE-2026-32175

## Summary
Severity: Medium
Advisory: CVE-2026-32175
Aliases: BIT-dotnet-2026-32175, BIT-dotnet-sdk-2026-32175, GHSA-rg75-q538-x34v
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-32175
Type: osv

## Details
A tampering vulnerability exists when .NET Core improperly handles specially crafted files. An attacker who successfully exploited this vulnerability could write arbitrary files and directories to certain locations on a vulnerable system. However, an attacker would have limited control over the destination of the files and directories.
To exploit the vulnerability, an attacker must send a specially crafted file to a vulnerable system.
The security update fixes the vulnerability by ensuring .NET Core properly handles files.

## References
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-32175
