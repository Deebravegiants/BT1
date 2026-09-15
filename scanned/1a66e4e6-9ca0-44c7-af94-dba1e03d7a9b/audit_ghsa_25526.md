# [H] Command injection in cocoapods-downloader

## Summary
Severity: High
Advisory: GHSA-g397-v4w5-4m79
CVE: CVE-2022-21223
CWE: CWE-74, CWE-88
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-02
Source: https://github.com/advisories/GHSA-g397-v4w5-4m79
Type: github-advisory

## Affected
- RubyGems: `cocoapods-downloader` — affected >=0 <1.6.2

## Details
The package cocoapods-downloader before 1.6.2 are vulnerable to Command Injection via hg argument injection. When calling the download function (when using hg), the url (and/or revision, tag, branch) is passed to the hg clone command in a way that additional flags can be set. The additional flags can be used to perform a command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21223
- https://github.com/CocoaPods/cocoapods-downloader/pull/127
- https://github.com/CocoaPods/cocoapods-downloader
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/cocoapods-downloader/CVE-2022-21223.yml
- https://snyk.io/vuln/SNYK-RUBY-COCOAPODSDOWNLOADER-2414280
