# [C] CVE-2020-4068

## Summary
Severity: Critical
Advisory: CVE-2020-4068
Aliases: GHSA-qh2w-vjxg-mjcg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-4068
Type: osv

## Details
In APNSwift 1.0.0, calling APNSwiftSigner.sign(digest:) is likely to result in a heap buffer overflow. This has been fixed in 1.0.1.

## References
- https://github.com/kylebrowning/APNSwift/security/advisories/GHSA-qh2w-vjxg-mjcg
- https://github.com/kylebrowning/APNSwift/issues/31
- https://github.com/kylebrowning/APNSwift/pull/32
- https://github.com/kylebrowning/APNSwift/commit/97fa7f69dcdd89168fff84e0ba8f999881ee3d3f
