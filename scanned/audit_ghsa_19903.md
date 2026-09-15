# [H] PipeCD Vulnerable to Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-4jhw-c53w-w5r7
CVE: CVE-2024-53351
CWE: CWE-276, CWE-284, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-4jhw-c53w-w5r7
Type: github-advisory

## Affected
- Go: `github.com/pipe-cd/pipecd` — affected >=0

## Details
Insecure permissions in pipecd v0.49 allow attackers to gain access to the service account's token, leading to escalation of privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53351
- https://gist.github.com/HouqiyuA/948a808b8bd48b17b37a4d5e0b6fb005
- https://github.com/pipe-cd/pipecd
- https://pipecd.dev
