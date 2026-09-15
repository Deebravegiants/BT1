# [M] Parse Server has a login timing side-channel reveals user existence

## Summary
Severity: Medium
Advisory: GHSA-mmpq-5hcv-hf2v
CVE: CVE-2026-39321
CWE: CWE-208
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-mmpq-5hcv-hf2v
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.8.0-alpha.6
- npm: `parse-server` — affected >=0 <8.6.74

## Details
### Impact

The login endpoint response time differs measurably depending on whether the submitted username or email exists in the database. When a user is not found, the server responds immediately. When a user exists but the password is wrong, a bcrypt comparison runs first, adding significant latency. This timing difference allows an unauthenticated attacker to enumerate valid usernames.

### Patches

A dummy bcrypt comparison is now performed when no user is found, normalizing response timing regardless of user existence. Additionally, accounts without a stored password (e.g. OAuth-only) now also run a dummy comparison to prevent the same timing oracle.

### Workarounds

Configure rate limiting on the login endpoint to slow automated enumeration. This reduces throughput but does not eliminate the timing signal for individual requests.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-mmpq-5hcv-hf2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-39321
- https://github.com/parse-community/parse-server/pull/10398
- https://github.com/parse-community/parse-server/pull/10399
- https://github.com/parse-community/parse-server
