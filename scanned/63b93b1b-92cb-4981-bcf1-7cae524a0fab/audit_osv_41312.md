# [M] Timing Attack via Non-Constant-Time Comparison of Sensitive Values

## Summary
Severity: Medium
Advisory: CVE-2026-59276
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59276
Type: osv

## Details
Several components in Spring Security compare security-sensitive values using standard string equality (String.equals()) rather than a constant-time comparison. Because String.equals() returns as soon as it finds a differing character, the time taken to reject an incorrect value is proportional to the number of leading characters that match the expected value.
Spring Security 7.1.0
Spring Security 7.0.0 - 7.0.6
Spring Security 6.5.0 - 6.5.11
Spring Security 6.4.0 - 6.4.18
Spring Security 5.8.0 - 5.8.27
Spring Security 5.7.0 - 5.7.25

## References
- https://spring.io/security/cve-2026-59276
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59276.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59276
