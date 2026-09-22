# [H] Langflow Privilege Escalation

## Summary
Severity: High
Advisory: CVE-2024-7297
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-7297
Type: osv

## Details
Langflow versions prior to 1.0.13 suffer from a Privilege Escalation vulnerability, allowing a remote and low privileged attacker to gain super admin privileges by performing a mass assignment request on the '/api/v1/users' endpoint.

## References
- https://pypi.python.org
- https://www.tenable.com/security/research/tra-2024-26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7297.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7297
- https://github.com/langflow-ai/langflow
