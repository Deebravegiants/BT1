# [M] System.Management.Automation subject to bypass via script debugging

## Summary
Severity: Medium
Advisory: GHSA-5frh-8cmj-gc59
CVE: CVE-2019-1167
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-17
Source: https://github.com/advisories/GHSA-5frh-8cmj-gc59
Type: github-advisory

## Affected
- NuGet: `System.Management.Automation` — affected >=6.2.0 <6.2.2
- NuGet: `System.Management.Automation` — affected >=6.1.0 <6.1.5

## Details
## Microsoft Security Advisory CVE-2019-1167: Windows Defender Application Control Security Feature Bypass Vulnerability

# Microsoft Security Advisory CVE-2019-1167: Windows Defender Application Control Security Feature Bypass Vulnerability

## Executive Summary

A security feature bypass vulnerability exists in Windows Defender Application Control (WDAC) which could allow an attacker to bypass WDAC enforcement.
An attacker who successfully exploited this vulnerability could circumvent PowerShell Core Constrained Language Mode on the machine.

 To exploit the vulnerability,
an attacker would first have access to the local machine where PowerShell is running in Constrained Language mode.
By doing that an attacker could leverage script debugging to abuse signed modules in an unintended way.

The update addresses the vulnerability by correcting how PowerShell functions in Constrained Language Mode.
System administrators are advised to update PowerShell Core to an unaffected version (see [affected software](#user-content-affected-software).)

## Discussion

Please use PowerShell/PowerShell#TBD for discussion of this advisory.

## <a name="affected-software">Affected Software</a>

The vulnerability affects PowerShell Core prior to the following versions:

| PowerShell Core Version | Fixed in          |
|-------------------------|-------------------|
| 6.1                     | 6.1.5               |
| 6.2                     | 6.2.2               |

## Advisory FAQ

### How do I know if I am affected?

If all of the following are true:

1. Run `pwsh -v`, then, check the version in the table in [Affected Software](#user-content-affected-software) to see if your version of PowerShell Core is affected.
1. If you are running a version of PowerShell Core where the executable is not `pwsh` or `pwsh.exe`, then you are affected.  This only existed for preview version of `6.0`.

### How do I update to an unaffected version?

Follow the instructions at [Installing PowerShell Core](https://docs.microsoft.com/en-us/powershell/scripting/setup/installing-powershell?view=powershell-6) to install the latest version of PowerShell Core.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in PowerShell Core,
please email details to secure@microsoft.com.

### Support

You can ask questions about this issue on GitHub in the PowerShell organization.
This is located at https://github.com/PowerShell/.
The Announcements repo (https://github.com/PowerShell/Announcements)
will contain this bulletin as an issue and will include a link to a discussion issue where you can ask questions.

### What if the update breaks my script or module?

You can uninstall the newer version of PowerShell Core and install the previous version of PowerShell Core.
This should be treated as a temporary measure.
Therefore, the script or module should be updated to work with the patched version of PowerShell Core.

### Acknowledgments

Microsoft recognizes the efforts of those in the security community who help us protect customers through coordinated vulnerability disclosure.

See [acknowledgments](https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments) for more information.

### External Links

[CVE-2019-1167](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1167)

### Revisions

V1.0 (July 16, 2019): Advisory published.

*Version 1.0*
*Last Updated 2019-07-16*

## References
- https://github.com/PowerShell/PowerShell/security/advisories/GHSA-5frh-8cmj-gc59
- https://nvd.nist.gov/vuln/detail/CVE-2019-1167
- https://github.com/advisories/GHSA-5frh-8cmj-gc59
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1167
