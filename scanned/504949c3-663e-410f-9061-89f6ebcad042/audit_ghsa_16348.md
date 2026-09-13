# [H] ZenML Server Remote Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-vf7j-cmrj-pmmm
CVE: CVE-2024-25723
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-vf7j-cmrj-pmmm
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.42.2
- PyPI: `zenml` — affected >=0.43.0 <0.43.1
- PyPI: `zenml` — affected >=0.45.0 <0.46.7
- PyPI: `zenml` — affected >=0.44.0 <0.44.4

## Details
ZenML Server in the ZenML package before 0.46.7 for Python allows remote privilege escalation because the `/api/v1/users/{user_name_or_id}/activate` REST API endpoint allows access on the basis of a valid username along with a new password in the request body. These are also patched versions: 0.44.4, 0.43.1, and 0.42.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25723
- https://github.com/zenml-io/zenml
- https://github.com/zenml-io/zenml/compare/0.42.1...0.42.2
- https://github.com/zenml-io/zenml/compare/0.43.0...0.43.1
- https://github.com/zenml-io/zenml/compare/0.44.3...0.44.4
- https://www.zenml.io/blog/critical-security-update-for-zenml-users
