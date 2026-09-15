# [M] wire-ios accidentally logs message contents

## Summary
Severity: Medium
Advisory: CVE-2025-49846
Aliases: GHSA-pj5p-96xx-hc7m
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-49846
Type: osv

## Details
wire-ios is an iOS client for the Wire secure messaging application. From Wire iOS 3.111.1 to before 3.124.1, messages that were visible in the view port have been logged to the iOS system logs in clear text. Wire application logs created and managed by the application itself were not affected, especially not the logs users can export and send to Wire support. The iOS logs can only be accessed if someone had (physical) access to the underlying unlocked device. The issue manifested itself by calling canOpenUrl() and passing an invalid URL object. When iOS then performs the check and fails, it logs the contents to the system log. This is not documented behaviour. Wire released an emergency fix with version 3.124.1. As a workaround, users can reset their iOS device to remove the offending logs. Since Wire cannot access or modify iOS system logs, there's no other workaround other than a reset.

## References
- https://github.com/wireapp/wire-ios/releases/tag/appstore%2F3.124.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49846.json
- https://github.com/wireapp/wire-ios/security/advisories/GHSA-pj5p-96xx-hc7m
- https://nvd.nist.gov/vuln/detail/CVE-2025-49846
- https://github.com/wireapp/wire-ios/commit/0cff0e4298d87c2c56de07f3fb18d3e8e5a68fa3
