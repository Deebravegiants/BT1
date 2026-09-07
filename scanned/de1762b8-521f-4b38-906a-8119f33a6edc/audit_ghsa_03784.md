# [H] High severity vulnerability that affects System.Management.Automation

## Summary
Severity: High
Advisory: GHSA-62gw-3rmj-wmp2
CVE: CVE-2019-1301
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-09-13
Source: https://github.com/advisories/GHSA-62gw-3rmj-wmp2
Type: github-advisory

## Affected
- NuGet: `System.Management.Automation` — affected >=6.2.0 <6.2.3
- NuGet: `System.Management.Automation` — affected >=6.0.0 <6.1.6

## Details
# Microsoft Security Advisory CVE-2019-1301: Denial of Service Vulnerability in PowerShell Core

## Executive Summary

A denial of service vulnerability exists when PowerShell Core or .NET Core improperly handles web requests. An attacker who successfully exploited this vulnerability could cause a denial of service against a PowerShell Core scripts.

The update addresses the vulnerability by correcting how the .NET Core handles web requests.

System administrators are advised to update PowerShell Core to an unaffected version (see [affected software](#user-content-affected-software).)


## Discussion

Please [open a support question](https://github.com/PowerShell/PowerShell/issues/new?assignees=&labels=Issue-Question&template=Support_Question.md&title=Support+Question) to discussion the PowerShell aspects of this advisory.
Please use dotnet/announcements#121 for discussion of the .NET aspects this advisory.

## <a name="affected-software">Affected Software</a>

The vulnerability affects PowerShell Core prior to the following versions:


| PowerShell Core Version | Fixed in          |
|-------------------------|-------------------|
| 6.1                     | 6.1.6               |
| 6.2                     | 6.2.3               |
| 7.0                     | unaffected               |
|5                      | unaffected   |

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

Paul Ryman of VMware Sydney Engineering Team

Microsoft recognizes the efforts of those in the security community who help us protect customers through coordinated vulnerability disclosure.

See [acknowledgments](https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments) for more information.

### External Links

[CVE-2019-1301](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1301)

## References
- https://github.com/PowerShell/PowerShell/security/advisories/GHSA-62gw-3rmj-wmp2
- https://nvd.nist.gov/vuln/detail/CVE-2019-1301
- https://github.com/PowerShell/PowerShell
- https://github.com/advisories/GHSA-62gw-3rmj-wmp2
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1301
