# [M] wire-ios has Persistent Remote DoS via Integer Underflow

## Summary
Severity: Medium
Advisory: CVE-2026-35049
Aliases: GHSA-v6wg-c7qc-x66g
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-35049
Type: osv

## Details
wire-ios is an iOS client for the Wire secure messaging application. Prior to version 4.16.0, upon receiving a crafted malicious Proteus external message with an encrypted payload that is shorter than 16 bytes, the Wire iOS client crashes. The crash is triggered automatically after message receival with no user interaction. Since the malicious message persists in the conversation, the app enters a crash loop on relaunch and cannot be reopened until the local state is wiped. This issue has been fixed with version 4.16.0 which introduces the missing length check and is available via the App Store. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35049.json
- https://github.com/wireapp/wire-ios/security/advisories/GHSA-v6wg-c7qc-x66g
- https://nvd.nist.gov/vuln/detail/CVE-2026-35049
