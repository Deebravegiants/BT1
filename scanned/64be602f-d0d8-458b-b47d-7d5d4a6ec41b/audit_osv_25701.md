# [H] Chamilo LMS Learning Path PPT2LP Command Injection Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-4221
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-28
Source: https://osv.dev/vulnerability/CVE-2023-4221
Type: osv

## Details
Command injection in `main/lp/openoffice_presentation.class.php` in Chamilo LMS <= v1.11.24 allows users permitted to upload Learning Paths to obtain remote code execution via improper neutralisation of special characters.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4221.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4221
- https://starlabs.sg/advisories/23/23-4221
- https://support.chamilo.org/projects/chamilo-18/wiki/security_issues#Issue-128-2023-09-04-Critical-impact-Moderate-risk-Authenticated-users-may-gain-unauthenticated-RCE-CVE-2023-4221CVE-2023-4222
- https://github.com/chamilo/chamilo-lms/commit/841a07396fed0ef27c5db13a1b700eac02754fc7
- https://github.com/chamilo/chamilo-lms/commit/ed72914608d2a07ee2eb587c1a654480d08201db
