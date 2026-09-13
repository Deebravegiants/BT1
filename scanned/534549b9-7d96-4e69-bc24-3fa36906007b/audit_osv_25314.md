# [C] Chamilo LMS Unauthenticated Command Injection

## Summary
Severity: Critical
Advisory: CVE-2023-3368
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-28
Source: https://osv.dev/vulnerability/CVE-2023-3368
Type: osv

## Details
Command injection in `/main/webservices/additional_webservices.php` in Chamilo LMS <= v1.11.20 allows unauthenticated attackers to obtain remote code execution via improper neutralisation of special characters. This is a bypass of CVE-2023-34960.

## References
- https://github.com/chamilo/chamilo-lms/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3368.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3368
- https://starlabs.sg/advisories/23/23-3368/
- https://support.chamilo.org/projects/chamilo-18/wiki/security_issues#Issue-121-2023-07-05-Critical-impact-High-risk-Unauthenticated-Command-Injection-CVE-2023-3368
- https://github.com/chamilo/chamilo-lms/commit/37be9ce7243a30259047dd4517c48ff8b21d657a
- https://https://github.com/chamilo/chamilo-lms/commit/4c69b294f927db62092e01b70ac9bd6e32d5b48b
