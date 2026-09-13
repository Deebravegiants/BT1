# [M] svix vulnerable to Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-747x-5m58-mq97
CVE: CVE-2024-21491
CWE: CWE-288, CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-747x-5m58-mq97
Type: github-advisory

## Affected
- crates.io: `svix` — affected >=0 <1.17.0

## Details
Versions of the package svix before 1.17.0 are vulnerable to Authentication Bypass due to an issue in the verify function where signatures of different lengths are incorrectly compared. An attacker can bypass signature verification by providing a shorter signature that matches the beginning of the actual signature.

**Note:**

The attacker would need to know a victim uses the Rust library for verification,no easy way to automatically check that; and uses webhooks by a service that uses Svix, and then figure out a way to craft a malicious payload that will actually include all of the correct identifiers needed to trick the receivers to cause actual issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21491
- https://github.com/svix/svix-webhooks/pull/1190
- https://github.com/svix/svix-webhooks/commit/958821bd3b956d1436af65f70a0964d4ffb7daf6
- https://github.com/svix/svix-webhooks
- https://rustsec.org/advisories/RUSTSEC-2024-0010.html
- https://security.snyk.io/vuln/SNYK-RUST-SVIX-6230729
