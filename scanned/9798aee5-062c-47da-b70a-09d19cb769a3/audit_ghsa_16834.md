# [H] Request smuggling leading to endpoint restriction bypass in Gunicorn

## Summary
Severity: High
Advisory: GHSA-w3h3-4rj7-4ph4
CVE: CVE-2024-1135
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-w3h3-4rj7-4ph4
Type: github-advisory

## Affected
- PyPI: `gunicorn` — affected >=0 <22.0.0

## Details
Gunicorn fails to properly validate Transfer-Encoding headers, leading to HTTP Request Smuggling (HRS) vulnerabilities. By crafting requests with conflicting Transfer-Encoding headers, attackers can bypass security restrictions and access restricted endpoints. This issue is due to Gunicorn's handling of Transfer-Encoding headers, where it incorrectly processes requests with multiple, conflicting Transfer-Encoding headers, treating them as chunked regardless of the final encoding specified. This vulnerability has been shown to allow access to endpoints restricted by gunicorn. This issue has been addressed in version 22.0.0.

To be affected users must have a network path which does not filter out invalid requests. These users are advised to block access to restricted endpoints via a firewall or other mechanism if they are unable to update.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1135
- https://github.com/benoitc/gunicorn/issues/3091
- https://github.com/benoitc/gunicorn/pull/3113
- https://github.com/benoitc/gunicorn/commit/ac29c9b0a758d21f1e0fb3b3457239e523fa9f1d
- https://github.com/benoitc/gunicorn
- https://github.com/benoitc/gunicorn/releases/tag/22.0.0
- https://huntr.com/bounties/22158e34-cfd5-41ad-97e0-a780773d96c1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00018.html
