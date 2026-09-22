# [H] tgstation-server cached user logins in legacy server

## Summary
Severity: High
Advisory: GHSA-42r6-p4px-qvv6
CVE: CVE-2018-17107
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-42r6-p4px-qvv6
Type: github-advisory

## Affected
- NuGet: `TGServiceInterface` — affected >=3.2.1.0 <3.2.5.0

## Details
Please note this advisory is for a historical preexisting issue in the legacy server from 2018. It has long since been triaged. It is being moved here for visibility. The text below is copied from the original issue #690

# You can login to the server with any username/password combination if someone else is logged in

An explanation of the bug: Back in 3.2.1.0, in order to accommodate running the Control Panel using Mono some hooks were added to the WCF communication layer. Detailed in this commit: https://github.com/tgstation/tgstation-server/commit/2894ea03d708c7f16bab47ba5020c2ad4c3d5554#diff-0ba090ea7073a3a304dfdbdfc512f733 

The bug was in this line: https://github.com/tgstation/tgstation-server/commit/2894ea03d708c7f16bab47ba5020c2ad4c3d5554#diff-0ba090ea7073a3a304dfdbdfc512f733R48
authPolicy is passed in by the framework but the documentation for what the parameter is is virtually non-existent: https://docs.microsoft.com/en-us/dotnet/api/system.servicemodel.serviceauthenticationmanager.authenticate?view=netframework-4.7.2#System_ServiceModel_ServiceAuthenticationManager_Authenticate_System_Collections_ObjectModel_ReadOnlyCollection_System_IdentityModel_Policy_IAuthorizationPolicy__System_Uri_System_ServiceModel_Channels_Message__

Turns out it is a cache of what the previously returned policy was, as Floyd thankfully found out for us. The security patch fixes the issue by creating a new empty list as the return value when password authentication fails as opposed to using the authPolicy parameter.

If you're wondering why this line: https://github.com/tgstation/tgstation-server/commit/2894ea03d708c7f16bab47ba5020c2ad4c3d5554#diff-0ba090ea7073a3a304dfdbdfc512f733R42 didn't prevent the issue. It only invalidated the actual Windows login session, but in the eyes of the server the user was still valid since we just passed that closed handle as a return result. Had access to static files been attempted with a bad login, the request would end up erroring due to trying to impersonate using a closed user token handle.

This has been fixed in 1812a9c6793c8516c138a105ccfb2108164f0eff and versions 3.2.5.0+

## References
- https://github.com/tgstation/tgstation-server/security/advisories/GHSA-42r6-p4px-qvv6
- https://nvd.nist.gov/vuln/detail/CVE-2018-17107
- https://github.com/tgstation/tgstation-server/commit/1812a9c6793c8516c138a105ccfb2108164f0eff
- https://github.com/tgstation/tgstation-server/commit/2894ea03d708c7f16bab47ba5020c2ad4c3d5554#diff-0ba090ea7073a3a304dfdbdfc512f733
- https://docs.microsoft.com/en-us/dotnet/api/system.servicemodel.serviceauthenticationmanager.authenticate?view=netframework-4.7.2#System_ServiceModel_ServiceAuthenticationManager_Authenticate_System_Collections_ObjectModel_ReadOnlyCollection_System_IdentityModel_Policy_IAuthorizationPolicy__System_Uri_System_ServiceModel_Channels_Message__
- https://github.com/tgstation/tgstation-server
- https://github.com/tgstation/tgstation-server/blob/tgstation-server-v3.2.5.0/TGS.Interface/TGS.Interface.nuspec
- https://www.nuget.org/packages/TGServiceInterface
