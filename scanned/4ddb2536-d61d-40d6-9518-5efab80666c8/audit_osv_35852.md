# [C] Principal/domain lookup without case normalization

## Summary
Severity: Critical
Advisory: CVE-2026-15617
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-15617
Type: osv

## Details
Logto performs principal lookup without normalizing email and identifier strings, enabling principal collision and unauthorized account access via case- or Unicode-different identities.

## References
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/libraries/verification-helpers/single-sign-on-guard.ts#L23-L33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15617.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15617
