# [M] CVE-2021-41094

## Summary
Severity: Medium
Advisory: CVE-2021-41094
Aliases: GHSA-h4m7-pr8h-j7rf
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/CVE-2021-41094
Type: osv

## Details
Wire is an open source secure messenger. Users of Wire by Bund may bypass the mandatory encryption at rest feature by simply disabling their device passcode. Upon launching, the app will attempt to enable encryption at rest by generating encryption keys via the Secure Enclave, however it will fail silently if no device passcode is set. The user has no indication that encryption at rest is not active since the feature is hidden to them. This issue has been resolved in version 3.70

## References
- https://github.com/wireapp/wire-ios/security/advisories/GHSA-h4m7-pr8h-j7rf
- https://github.com/wireapp/wire-ios/commit/5ba3eb180efc3fc795d095f9c84ae7f109b84746
