# [M] Arbitrary file read using percent-encoded relative paths in FileMiddleware

## Summary
Severity: Medium
Advisory: GHSA-vcvg-xgr8-p5gq
CVE: CVE-2020-15230
CWE: CWE-22
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-vcvg-xgr8-p5gq
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=4.0.0-rc.2.5 <4.29.4

## Details
### Impact

Attackers can access data at arbitrary filesystem paths on the same host as an application using `FileMiddleware`.

### Patches

Version [4.29.4](https://github.com/vapor/vapor/releases/tag/4.29.4)

### Workarounds

Upgrade to 4.24.4 or later, or disable `FileMiddleware`.

### References

* Introduced in https://github.com/vapor/vapor/pull/2223
* Fixed by https://github.com/vapor/vapor/pull/2500

### For more information

If you have any questions or comments about this advisory:
* Open [an issue](https://github.com/vapor/vapor/issues)
* Email us at [security@vapor.codes](mailto:security@vapor.codes)

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-vcvg-xgr8-p5gq
- https://nvd.nist.gov/vuln/detail/CVE-2020-15230
- https://github.com/vapor/vapor/pull/2500
- https://github.com/vapor/vapor/commit/cf1651f7ff76515593f4d8ca6e6e15d2247fe255
- https://github.com/vapor/vapor
