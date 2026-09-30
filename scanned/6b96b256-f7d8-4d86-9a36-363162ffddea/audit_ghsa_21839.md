# [M] Command injection in github.com/google/fscrypt

## Summary
Severity: Medium
Advisory: GHSA-wxjg-p59j-6c92
CVE: CVE-2022-25328
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-26
Source: https://github.com/advisories/GHSA-wxjg-p59j-6c92
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.3.3

## Details
The bash_completion script for fscrypt allows injection of commands via crafted mountpoint paths, allowing privilege escalation under a specific set of circumstances. A local user who has control over mountpoint paths could potentially escalate their privileges if they create a malicious mountpoint path and if the system administrator happens to be using the fscrypt bash completion script to complete mountpoint paths. We recommend upgrading to version 0.3.3 or above

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25328
- https://github.com/google/fscrypt/pull/346
- https://github.com/google/fscrypt
