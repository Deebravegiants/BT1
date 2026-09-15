# [M] DoS vulnerability: Invalid Accent Colors

## Summary
Severity: Medium
Advisory: CVE-2022-31009
Aliases: GHSA-83m6-p7x5-925j
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-23
Source: https://osv.dev/vulnerability/CVE-2022-31009
Type: osv

## Details
wire-ios is an iOS client for the Wire secure messaging application. Invalid accent colors of Wire communication partners may render the iOS Wire Client partially unusable by causing it to crash multiple times on launch. These invalid accent colors can be used by and sent between Wire users. The root cause was an unnecessary assert statement when converting an integer value into the corresponding enum value, causing an exception instead of a fallback to a default value. This issue is fixed in [wire-ios](https://github.com/wireapp/wire-ios/commit/caa0e27dbe51f9edfda8c7a9f017d93b8cfddefb) and in Wire for iOS 3.100. There is no workaround available, but users may use other Wire clients (such as the [web app](https://app.wire.com)) to continue using Wire, or upgrade their client.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31009.json
- https://github.com/wireapp/wire-ios/security/advisories/GHSA-83m6-p7x5-925j
- https://nvd.nist.gov/vuln/detail/CVE-2022-31009
- https://github.com/wireapp/wire-ios/commit/caa0e27dbe51f9edfda8c7a9f017d93b8cfddefb
