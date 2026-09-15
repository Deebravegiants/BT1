# [C] Microsoft Security Advisory CVE-2026-40372 – ASP.NET Core Elevation of Privilege

## Summary
Severity: Critical
Advisory: GHSA-9mv3-2cwr-p262
CVE: CVE-2026-40372
CWE: CWE-347
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-9mv3-2cwr-p262
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.DataProtection` — affected >=10.0.0 <10.0.7

## Details
## Executive Summary: 

A bug in `Microsoft.AspNetCore.DataProtection` 10.0.0-10.0.6 NuGet packages can give an attacker the opportunity to execute an Elevation of Privilege attack by forging authentication cookies, and also allows some protected payloads to be decrypted.

If an attacker used forged payloads to authenticate as a privileged user during the vulnerable window, they may have induced the application to issue **legitimately-signed** tokens (session refresh, API key, password reset link, etc.) to themselves. Those tokens remain valid after upgrading to 10.0.7 unless the DataProtection key ring is rotated.

This is comparable in capability to [MS10-070](https://learn.microsoft.com/en-us/security-updates/SecurityBulletins/2010/ms10-070), which exploited a similar padding-oracle condition in ASP.NET's legacy encryption infrastructure.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/395

## CVSS Details

- **Version:** 3.1
- **Severity:** Important
- **Score:** 9.1
- **Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N
- **Weakness:** CWE-347: Improper Verification of Cryptographic Signature

## Affected Platforms

- **Platforms:** All
- **Architectures:** All

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects some Microsoft .NET projects if they use any of affected package versions listed below

### <a name="ASP.NET Core 10"></a>ASP.NET Core 10
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.DataProtection](https://www.nuget.org/packages/Microsoft.AspNetCore.DataProtection)               | >=10.0.0, <=10.0.6 | 10.0.7

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?
 
#### Primary affected configuration (10.0.6 on `net10.0`)
 
You are **affected** if ALL of the following are true:
 
- Your application referenced `Microsoft.AspNetCore.DataProtection` version 10.0.6 from NuGet (directly or transitively via, e.g., `Microsoft.AspNetCore.DataProtection.StackExchangeRedis`, `.EntityFrameworkCore`, `.AzureKeyVault`, `.AzureStorage`, `.Redis`), AND
The affected 10.0.6 NuGet binary was actually loaded at runtime. This happens when either the application does NOT target the Microsoft.NET.Sdk.Web NOR has a Microsoft.AspNetCore.App framework reference either directly or transitively UNLESS you opt out of PrunePackageReference which is enabled by default in .NET 10. 
- The application ran on Linux, macOS, or any non-Windows operating system.
 
#### Secondary affected configuration (10.0.x on `net462` / `netstandard2.0`)

You are also affected if:
 
- Your application or library referenced `Microsoft.AspNetCore.DataProtection` versions 10.0.0 through 10.0.6 from NuGet, AND
- The build consumed the `net462` or `netstandard2.0` target framework asset of that package. This occurs when your application does not target `net10.0` and consumes the package (e.g. `net8.0`, `net9.0`, `net481` for mono, etc.). This combination is unusual because 10.0 NuGet packages are generally intended for use with .NET 10.
 
This secondary population is much smaller and is expected to primarily consist of:
- Desktop or server applications on .NET Framework that happen to use the ASP.NET Core DataProtection NuGet package.
- Libraries that target `netstandard2.0` and reference the 10.0 DataProtection package.
 
These configurations use the same managed authenticated encryptor code path on all operating systems (the CNG path is only available on the `net10.0` asset), so the Windows exception below does not apply to them.
 
#### Not affected
 
- Your application runs on **Windows** 
- Your application runs **framework-dependent** on `net10.0` and your installed ASP.NET Core shared framework version is **≥** your PackageReference version of `Microsoft.AspNetCore.DataProtection`. In this case the (correct) shared framework copy is loaded and the NuGet copy is not used. For example, shared framework 10.0.6 + PackageReference 10.0.6 is safe; shared framework 10.0.5 + PackageReference 10.0.6 is not.
- Your application uses `Microsoft.AspNetCore.DataProtection` **8.0.x or 9.0.x** from NuGet, on any target framework, any operating system, any shared framework version. The defective code path was introduced during 10.0 development and was never backported to the 8.0 or 9.0 servicing branches.
- Your application never referenced any affected version of the package.

### <a name="how-fix"></a>How do I fix the issue?

1. **Upgrade `Microsoft.AspNetCore.DataProtection` to 10.0.7 or later** and redeploy. This fixes the validation routine. Any forged payloads produced during the vulnerable window (which necessarily carried all-zero HMAC bytes) will be rejected by the corrected code.
 
2. **Rotate the DataProtection key ring** if your application was affected and served internet-exposed endpoints during the vulnerable window. This invalidates any legitimately-signed tokens the application may have issued to attackers during that period.
 
   Example using the built-in key manager:
 
   ```csharp
   // Run once, from an application with access to the same key ring.
   // Replace the cutoff with a timestamp just before you deployed 10.0.6.
   var services = new ServiceCollection()
       .AddDataProtection()
       // ... your existing repository / protection configuration ...
       .Services
       .BuildServiceProvider();
 
   var keyManager = services.GetRequiredService<IKeyManager>();
   keyManager.RevokeAllKeys(
       revocationDate: DateTimeOffset.UtcNow,      // revoke all keys currently in the ring
       reason: "CVE-TBD: DataProtection 10.0.6 validation bypass");
   ```
 
   `RevokeAllKeys` marks every existing key as revoked; a new key is auto-generated on the next protect operation. All users will need to sign in again, all antiforgery tokens will be reissued, etc.
 
   If you can be more surgical — for instance, you know no key older than `T` was used by an affected process — use `RevokeKey(Guid keyId, string reason)` instead to revoke only the keys that were active during the vulnerable window.
 
3. **Audit application-level long-lived artifacts** that were created during the vulnerable window and carry identity or capability. These survive key rotation and must be rotated at the application layer:
   - API keys, refresh tokens, or access tokens stored in your database and issued via a protected endpoint.
   - Password reset links or email-confirmation tokens that were emitted during the window and have not yet expired.
   - Any other persistent capability that an authenticated request could have caused your application to issue.
 
   If your application does not issue such long-lived artifacts via authenticated endpoints, key rotation alone is sufficient.
 
### Recommended
 
4. **Audit plaintext stored inside protected payloads.** If your application stores long-lived secrets (database connection strings, third-party API keys, etc.) inside `IDataProtector.Protect` output, treat those secrets as potentially disclosed and rotate them at their respective sources.
 
5. **Review web server logs** for anomalous request volume against endpoints that accept protected payloads (auth cookies, antiforgery tokens, state parameters). The padding-oracle attack requires many requests per byte recovered — orders of magnitude more than normal traffic for that endpoint. Sustained high-volume traffic with varying cookie/query-parameter values against a single authenticated endpoint during the vulnerable window is a strong indicator.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in a supported version of .NET, please report it to the Microsoft Security Response Center (MSRC) via the [MSRC Researcher Portal](https://msrc.microsoft.com/report/vulnerability/new). Further information can be found in the MSRC [Report an Issue FAQ](https://www.microsoft.com/msrc/faqs-report-an-issue).

Security reports made through MSRC may qualify for the Microsoft .NET Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at https://aka.ms/corebounty.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main ASP.NET Core repo is located at https://github.com/dotnet/aspnetcore. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2026-40372]( https://www.cve.org/CVERecord?id=CVE-2026-40372)

### Revisions

V1.0 (April 21, 2026): Advisory published.

## References
- https://github.com/dotnet/aspnetcore/security/advisories/GHSA-9mv3-2cwr-p262
- https://nvd.nist.gov/vuln/detail/CVE-2026-40372
- https://github.com/dotnet/announcements/issues/395
- https://github.com/dotnet/aspnetcore
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-40372
