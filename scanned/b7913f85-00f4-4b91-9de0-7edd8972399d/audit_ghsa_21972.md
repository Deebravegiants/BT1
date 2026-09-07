# [M] User login denial of service in github.com/google/fscrypt

## Summary
Severity: Medium
Advisory: GHSA-8vwm-8vj8-rqjf
CVE: CVE-2022-25327
CWE: CWE-276
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-26
Source: https://github.com/advisories/GHSA-8vwm-8vj8-rqjf
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.3.3

## Details
The PAM module for fscrypt doesn't adequately validate fscrypt metadata files, allowing users to create malicious metadata files that prevent other users from logging in. A local user can cause a denial of service by creating a fscrypt metadata file that prevents other users from logging into the system. We recommend upgrading to version 0.3.3 or above

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25327
- https://github.com/google/fscrypt/pull/346
- https://github.com/google/fscrypt/commit/91aa3ebf42032ca783c41f9ec25d885875f66ddb
- https://github.com/google/fscrypt
