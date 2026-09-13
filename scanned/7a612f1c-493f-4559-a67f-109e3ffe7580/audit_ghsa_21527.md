# [M] Remote code execution vulnerability in dependency System.Drawing.Common

## Summary
Severity: Medium
Advisory: GHSA-gpv5-rp6w-58r8
Ecosystem: NuGet
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-gpv5-rp6w-58r8
Type: github-advisory

## Affected
- NuGet: `Akka` — affected >=0 <1.4.46
- NuGet: `Akka` — affected >=1.5.0-alpha1 <1.5.0-alpha3

## Details
### Impact

The core Akka module depended on an old System.Configuration.ConfigurationManager version 4.7.0 which transitively depends on System.Common.Drawing v4.7.0. The System.Common.Drawing v4.7.0 is affected by a remote code execution vulnerability https://github.com/advisories/GHSA-ghhp-997w-qr28.

The real-world impact of this should be low, but users should be advised to upgrade to later versions of Akka.NET.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

This issue is resolved in Akka.NET v1.4.46 and Akka.NET v1.5.0-alpha3.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

You might be able to explicitly reference System.Configuration.ConfigurationManager's NuGet package and upgrade to 6.0.1 or later without upgrading Akka.NET, but it's probably best to upgrade Akka.NET itself.

### References
_Are there any links users can visit to find out more?_

Original issue: https://github.com/akkadotnet/akka.net/issues/6226
MSFT advisory: https://github.com/advisories/GHSA-ghhp-997w-qr28

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [the Akka.NET repository](https://github.com/akkadotnet/akka.net/issues/new)
* Contact us on [the Akka.NET Discord](https://discord.gg/GSCfPwhbWP)

## References
- https://github.com/akkadotnet/akka.net/security/advisories/GHSA-gpv5-rp6w-58r8
- https://github.com/akkadotnet/akka.net
