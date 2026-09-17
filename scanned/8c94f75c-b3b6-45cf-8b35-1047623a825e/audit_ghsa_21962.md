# [M] Uncontrolled Resource Consumption in github.com/google/fscrypt

## Summary
Severity: Medium
Advisory: GHSA-mpq4-rjj8-fjph
CVE: CVE-2022-25326
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-26
Source: https://github.com/advisories/GHSA-mpq4-rjj8-fjph
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.3.3

## Details
fscrypt through v0.3.2 creates a world-writable directory by default when setting up a filesystem, allowing unprivileged users to exhaust filesystem space. We recommend upgrading to fscrypt 0.3.3 or above and adjusting the permissions on existing fscrypt metadata directories where applicable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25326
- https://github.com/google/fscrypt/pull/346
- https://github.com/google/fscrypt/commit/91aa3ebf42032ca783c41f9ec25d885875f66ddb
- https://github.com/google/fscrypt
