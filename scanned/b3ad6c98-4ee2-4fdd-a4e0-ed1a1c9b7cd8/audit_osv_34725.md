# [C] ELOG user profile missing authorization

## Summary
Severity: Critical
Advisory: CVE-2025-64349
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-64349
Type: osv

## Details
ELOG allows an authenticated user to modify another user's profile. An attacker can edit a target user's email address, then request a password reset, and take control of the target account. By default, ELOG is not configured to allow self-registration.

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-25-304-01.json
- https://www.cve.org/CVERecord?id=CVE-2025-64349
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64349.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64349
- https://bitbucket.org/ritt/elog/commits/7092ff64f6eb9521f8cc8c52272a020bf3730946
- https://bitbucket.org/ritt/elog/commits/f81e5695c40997322fe2713bfdeba459d9de09dc
