# [H] PowerShell is subject to remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-jcmq-5rrv-j2g4
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-jcmq-5rrv-j2g4
Type: github-advisory

## Affected
- NuGet: `PowerShell` — affected >=0 <7.0.0

## Details
# Microsoft Security Advisory CVE-2020-0605: .NET Framework Remote Code Execution Vulnerability

## Executive Summary

A remote code execution vulnerability exists in .NET software when the software fails to check the source markup of a file.

An attacker who successfully exploited the vulnerability could run arbitrary code in the context of the current user. If the current user is logged on with administrative user rights, an attacker could take control of the affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights. Users whose accounts are configured to have fewer user rights on the system could be less impacted than users who operate with administrative user rights.

Exploitation of the vulnerability requires that a user open a specially crafted file with an affected version of .NET Framework. In an email attack scenario, an attacker could exploit the vulnerability by sending the specially crafted file to the user and convincing the user to open the file.

The security update addresses the vulnerability by correcting how .NET Framework checks the source markup of a file.

## Discussion

Please [open a support question](https://github.com/PowerShell/PowerShell/issues/new?assignees=&labels=Issue-Question&template=Support_Question.md&title=Support+Question) to discuss the PowerShell aspects of this advisory.
Please use https://github.com/dotnet/wpf/issues/2424 for discussion of the .NET WPF aspects of this advisory.

## <a name="affected-software">Affected Software</a>

The vulnerability affects PowerShell prior to the following versions:

| PowerShell Core Version | Fixed in          |
|-------------------------|-------------------|
| 6.2                     | Not Affected              |
| 7.0                     | 7.0.0              |
## Advisory FAQ

### How do I know if I am affected?

If all of the following are true:

1. Run `pwsh -v`, then, check the version in the table in [Affected Software](#user-content-affected-software) to see if your version of PowerShell is affected.
1. If you are running a version of PowerShell where the executable is not `pwsh` or `pwsh.exe`, then you are affected.  This only existed for preview version of `7.0`.

### How do I update to an unaffected version?

Follow the instructions at [Installing PowerShell](https://docs.microsoft.com/en-us/powershell/scripting/setup/installing-powershell?view=powershell-7) to install the latest version of PowerShell.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in PowerShell,
please email details to secure@microsoft.com.

### Support

You can ask questions about this issue on GitHub in the PowerShell organization.
This is located at https://github.com/PowerShell/.
The Announcements repo (https://github.com/PowerShell/Announcements)
will contain this bulletin as an issue and will include a link to a discussion issue where you can ask questions.

### What if the update breaks my script or module?

You can uninstall the newer version of PowerShell and install the previous version of PowerShell.
This should be treated as a temporary measure.
Therefore, the script or module should be updated to work with the patched version of PowerShell.

### Acknowledgments

Soroush Dalili ([@irsdl](https://twitter.com/irsdl))

### External Links

[CVE-2020-0605](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0605)

### Revisions

<!-- TBD: update date -->
V1.0 (March 10, 2020): Advisory published.

*Version 1.0*
*Last Updated 2020-03-10*

## References
- https://github.com/PowerShell/PowerShell/security/advisories/GHSA-jcmq-5rrv-j2g4
