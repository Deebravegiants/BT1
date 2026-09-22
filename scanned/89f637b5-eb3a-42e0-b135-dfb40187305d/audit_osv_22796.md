# [H] Combodo iTop's weak password reset token leads to account takeover

## Summary
Severity: High
Advisory: CVE-2022-39216
Aliases: GHSA-hggq-48p2-cmhm
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2022-39216
Type: osv

## Details
Combodo iTop is an open source, web-based IT service management platform. Prior to versions 2.7.8 and 3.0.2-1, the reset password token is generated without any randomness parameter. This may lead to account takeover. The issue is fixed in versions 2.7.8 and 3.0.2-1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39216.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-hggq-48p2-cmhm
- https://nvd.nist.gov/vuln/detail/CVE-2022-39216
- https://github.com/Combodo/iTop/commit/35a8b501c9e4e767ec4b36c2586f34d4ab66d229
- https://github.com/Combodo/iTop/commit/f10e9c2d64d0304777660a4f70f1e80850ea864b
