# [H] Data races in conquer-once

## Summary
Severity: High
Advisory: GHSA-3jc5-5hc5-33gj
CVE: CVE-2020-36208
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3jc5-5hc5-33gj
Type: github-advisory

## Affected
- crates.io: `conquer-once` — affected >=0 <0.3.2

## Details
Affected versions of conquer-once implements Sync for its OnceCell type without restricting it to Sendable types.

This allows non-Send but Sync types such as MutexGuard to be sent across threads leading to undefined behavior and memory corruption in concurrent programs.

The issue was fixed by adding a Send constraint to OnceCell.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36208
- https://github.com/oliver-giersch/conquer-once/issues/3
- https://github.com/oliver-giersch/conquer-once
- https://rustsec.org/advisories/RUSTSEC-2020-0101.html
