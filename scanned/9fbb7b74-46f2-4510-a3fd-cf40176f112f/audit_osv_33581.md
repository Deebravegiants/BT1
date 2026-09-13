# [M] CVE-2025-46687

## Summary
Severity: Medium
Advisory: CVE-2025-46687
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2025-04-27
Source: https://osv.dev/vulnerability/CVE-2025-46687
Type: osv

## Details
quickjs-ng through 0.9.0 has a missing length check in JS_ReadString for a string, leading to a heap-based buffer overflow. QuickJS before 2025-04-26 is also affected.

## References
- https://bellard.org/quickjs/Changelog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46687.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46687
- https://github.com/bellard/quickjs/issues/399
- https://github.com/quickjs-ng/quickjs/issues/1018
- https://github.com/bellard/quickjs/commit/1eb05e44fad89daafa8ee3eb74b8520b4a37ec9a
- https://github.com/quickjs-ng/quickjs/commit/28fa43d3ddff2c1ba91b6e3a788b2d7ba82d1465
- https://github.com/quickjs-ng/quickjs/pull/1020
