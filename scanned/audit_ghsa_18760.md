# [H] Zitadel allows brute-forcing authentication factors

## Summary
Severity: High
Advisory: GHSA-xrw9-r35x-x878
CVE: CVE-2025-64102
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-xrw9-r35x-x878
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel/v2` — affected >=0 <2.71.18
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20251029090735-b8db8cdf9cc8

## Details
### Summary

A vulnerability in Zitadel allowed brute-force attack on OTP, TOTP and password allowing to impersonate the attacked user.

### Impact

An attacker can perform an online brute-force attack on OTP, TOTP, and passwords. While Zitadel allows preventing online brute force attacks in scenarios like TOTP, Email OTP, or passwords using a lockout mechanism. The mechanism is not enabled by default and can cause a denial of service for the corresponding user if enabled. Additionally, the mitigation strategies were not fully implemented in the more recent resource-based APIs.

### Affected Versions

All versions within the following ranges, including release candidates (RCs), are affected:
- **4.x**: `4.0.0` to `4.4.0` (including RC versions)
- **3.x**: `3.0.0` to `3.4.2` (including RC versions)
- **2.x**: `v2.0.0` to `2.71.17`

### Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by enforcing the lockout policy on all OTP, TOTP and password checks. Additionally a “tar pit” has been introduced to slow down brute-force attacks by default. Zitadel responses will be delayed by t seconds, where t increases over the number of failed attempts within a given timeframe.

4.x: Upgrade to >=[4.6.0](https://github.com/zitadel/zitadel/releases/tag/v4.6.0)
3.x: Update to >=[3.4.3](https://github.com/zitadel/zitadel/releases/tag/v3.4.3)
2.x: Update to >=[2.71.18](https://github.com/zitadel/zitadel/releases/tag/v2.71.18)

### Workarounds

The recommended solution is to update Zitadel to a patched version.

The problem might be mitigated by enabling the optional logout policy ("Password maximum attempts") or by implementing more strict rate limits.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

This vulnerability was found by [zentrust partners GmbH](https://zentrust.partners) during a scheduled penetration test. Thank you to the analysts Martin Tschirsich, Joud Zakharia, Christopher Baumann.
The full report will be made public after the complete review.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-xrw9-r35x-x878
- https://nvd.nist.gov/vuln/detail/CVE-2025-64102
- https://github.com/zitadel/zitadel/commit/b8db8cdf9cc8ea13f461758aef12457f8b7d972a
- https://github.com/zitadel/zitadel
- https://pkg.go.dev/vuln/GO-2025-4085
