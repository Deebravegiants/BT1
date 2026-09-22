# [M] CVE-2021-21301

## Summary
Severity: Medium
Advisory: CVE-2021-21301
Aliases: GHSA-7fg4-x8vj-qvxf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-11
Source: https://osv.dev/vulnerability/CVE-2021-21301
Type: osv

## Details
Wire is an open-source collaboration platform. In Wire for iOS (iPhone and iPad) before version 3.75 there is a vulnerability where the video capture isn't stopped in a scenario where a user first has their camera enabled and then disables it. It's a privacy issue because video is streamed to the call when the user believes it is disabled. It impacts all users in video calls. This is fixed in version 3.75.

## References
- https://github.com/wireapp/wire-ios/commit/7e3c30120066c9b10e50cc0d20012d0849c33a40
- https://github.com/wireapp/wire-ios/pull/4879
- https://github.com/wireapp/wire-ios/security/advisories/GHSA-7fg4-x8vj-qvxf
