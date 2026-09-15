# [C] Crawlab Missing Authorization on Password Change Endpoint Allows Account Takeover

## Summary
Severity: Critical
Advisory: CVE-2026-75103
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75103
Type: osv

## Details
Crawlab fails to verify user ownership or administrative role on the password-change endpoint, allowing any authenticated user to reset any account's password. Attackers can enumerate user accounts through the user listing endpoint and change administrator credentials to achieve full account takeover and arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75103.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75103
- https://www.vulncheck.com/advisories/crawlab-missing-authorization-on-password-change-endpoint-allows-account-takeover
- https://github.com/crawlab-team/crawlab/issues/1623
- https://github.com/crawlab-team/crawlab
- https://github.com/crawlab-team/crawlab/blob/main/core/controllers/user_v2.go
