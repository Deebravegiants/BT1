# [H] fastschema - TOCTOU Race Condition Bypasses OTP Attempt Limit in Account Recovery

## Summary
Severity: High
Advisory: CVE-2026-72584
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72584
Type: osv

## Details
A time-of-check/time-of-use (TOCTOU) race condition in fastschema through v0.15.1 allows an unauthenticated remote attacker to bypass the OTP attempt limit on the account recovery flow, enabling brute-force attacks on 6-digit OTP codes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72584.json
- https://github.com/fastschema/fastschema
- https://nvd.nist.gov/vuln/detail/CVE-2026-72584
- https://github.com/fastschema/fastschema/blob/main/pkg/auth/local.go
