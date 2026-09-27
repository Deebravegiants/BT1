# [M] Static Web Server affected by timing-based username enumeration in Basic Authentication due to early response on invalid usernames

## Summary
Severity: Medium
Advisory: GHSA-qhp6-635j-x7r2
CVE: CVE-2026-27480
CWE: CWE-204
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-qhp6-635j-x7r2
Type: github-advisory

## Affected
- crates.io: `static-web-server` — affected >=2.1.0 <2.41.0

## Details
## Summary

A Timing-based username enumeration in Basic Authentication vulnerability due to early response on invalid usernames could allow attackers to identify valid users and focus their efforts on targeted brute-force or credential-stuffing attacks.

## Details

SWS validates the provided username before performing any password verification.
- **Invalid Username:** The server returns a `401 Unauthorized` response immediately.
- **Valid Username:** The server proceeds to verify the password (e.g., using `bcrypt`), which introduces a different execution path and measurable timing discrepancy.

This allows an attacker to distinguish between existing and non-existing accounts by analyzing response times.

## PoC

The following statistical results were obtained by measuring the mean response time over 100 iterations using a custom Rust script:

| User Type | Average Response Time |
| :--- | :--- |
| **Invalid User** | 0.409861 ms |
| **Valid User** | 0.250925 ms |
| **Difference** | **~0.158936 ms** |

While the valid user responded faster in this specific test environment, the statistically significant gap confirms that the authentication logic does not execute in constant time.

## Impact

Users using the SWS' Basic Authentication feature are primarily impacted.

## References
- https://github.com/static-web-server/static-web-server/security/advisories/GHSA-qhp6-635j-x7r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27480
- https://github.com/static-web-server/static-web-server/commit/7bf0fd425eb10dac9bf9ef5febce12c4dd039ce1
- https://github.com/static-web-server/static-web-server
