# [M] CVE-2021-39169

## Summary
Severity: Medium
Advisory: CVE-2021-39169
Aliases: GHSA-pmmv-jwqh-f5ww
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-39169
Type: osv

## Details
Misskey is a decentralized microblogging platform. In versions of Misskey prior to 12.51.0, malicious actors can use the web client built-in dialog to display a malicious string, leading to cross-site scripting (XSS). XSS could compromise the API request token. This issue has been fixed in version 12.51.0. There are no known workarounds aside from upgrading.

## References
- https://github.com/misskey-dev/misskey/commit/ec203f7f795766f76b55fecc9248168c1cdf6c99
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-pmmv-jwqh-f5ww
