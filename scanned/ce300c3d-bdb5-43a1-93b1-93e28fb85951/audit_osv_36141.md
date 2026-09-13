# [M] iccDEV has Undefined Behavior (UB) - Invalid Enum Value

## Summary
Severity: Medium
Advisory: CVE-2026-21505
Aliases: GHSA-j577-8285-qrf9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21505
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV has undefined behavior due to an invalid enum value. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21505.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-j577-8285-qrf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-21505
- https://github.com/InternationalColorConsortium/iccDEV/issues/361
- https://github.com/InternationalColorConsortium/iccDEV/commit/3bbe2088b2796cf0aa4f7fa19f7ccd9ad1c7aba5
- https://github.com/InternationalColorConsortium/iccDEV/commit/b1bb72fc3e9442ee1355aabae7314bb7d3fc9d41
- https://github.com/InternationalColorConsortium/iccDEV/pull/419
