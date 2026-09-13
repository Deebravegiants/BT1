# [H] Command Injection

## Summary
Severity: High
Advisory: CVE-2022-24440
Aliases: GHSA-7627-mp87-jf6q, SNYK-RUBY-COCOAPODSDOWNLOADER-2414278
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-01
Source: https://osv.dev/vulnerability/CVE-2022-24440
Type: osv

## Details
The package cocoapods-downloader before 1.6.0, from 1.6.2 and before 1.6.3 are vulnerable to Command Injection via git argument injection. When calling the Pod::Downloader.preprocess_options function and using git, both the git and branch parameters are passed to the git ls-remote subcommand in a way that additional flags can be set. The additional flags can be used to perform a command injection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24440.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-24440
- https://snyk.io/vuln/SNYK-RUBY-COCOAPODSDOWNLOADER-2414278
- https://github.com/CocoaPods/cocoapods-downloader/pull/124
- https://github.com/CocoaPods/cocoapods-downloader/pull/128
