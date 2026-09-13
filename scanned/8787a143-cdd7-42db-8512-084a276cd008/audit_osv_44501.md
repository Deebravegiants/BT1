# [C] hulumi before v1.3.2 Privilege Escalation via IAM Policy

## Summary
Severity: Critical
Advisory: CVE-2026-82857
Aliases: GHSA-35qr-vx94-m5x3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82857
Type: osv

## Details
hulumi versions before v1.3.2 contain a privilege escalation vulnerability in the weekly integration IAM policy that allows role lifecycle operations on af-e2e-* roles without sufficient boundary restrictions. Attackers with the documented principal can create persistent higher-privilege roles in the sandbox account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82857.json
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-35qr-vx94-m5x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-82857
- https://www.vulncheck.com/advisories/hulumi-before-1.3.2-privilege-escalation-via-iam-policy
