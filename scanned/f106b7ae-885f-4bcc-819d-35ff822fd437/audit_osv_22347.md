# [M] CVE-2022-25883

## Summary
Severity: Medium
Advisory: CVE-2022-25883
Aliases: GHSA-c2qf-rxjj-qqgw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L/E:P)
Published: 2023-06-21
Source: https://osv.dev/vulnerability/CVE-2022-25883
Type: osv

## Details
Versions of the package semver before 7.5.2 are vulnerable to Regular Expression Denial of Service (ReDoS) via the function new Range, when untrusted user data is provided as a range.

## References
- https://github.com/npm/node-semver/blob/main/classes/range.js%23L97-L104
- https://github.com/npm/node-semver/blob/main/internal/re.js%23L138
- https://github.com/npm/node-semver/blob/main/internal/re.js%23L160
- https://security.snyk.io/vuln/SNYK-JS-SEMVER-3247795
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25883.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-25883
- https://security.netapp.com/advisory/ntap-20241025-0004/
- https://github.com/npm/node-semver/commit/717534ee353682f3bcf33e60a8af4292626d4441
- https://github.com/npm/node-semver/pull/564
