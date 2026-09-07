# [C] SwiftNIO SSL arbitrary code execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-frg3-gpcx-968f
CVE: CVE-2019-8849
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-frg3-gpcx-968f
Type: github-advisory

## Affected
- SwiftURL: `github.com/apple/swift-nio-ssl` — affected >=2.0.0 <2.4.1

## Details
A SwiftNIO application using TLS may be able to execute arbitrary code. The issue was addressed by signaling that an executable stack is not required. This issue is fixed in SwiftNIO SSL 2.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8849
- https://github.com/apple/swift-nio-ssl/commit/109faef770994e71b6bafcc015e2e96b88a4af8c
- https://github.com/apple/swift-nio-ssl
- https://github.com/apple/swift-nio-ssl/releases/tag/2.4.1
- https://security.snyk.io/vuln/SNYK-COCOAPODS-SWIFTNIOSSL-8492737
- https://support.apple.com/HT210772
