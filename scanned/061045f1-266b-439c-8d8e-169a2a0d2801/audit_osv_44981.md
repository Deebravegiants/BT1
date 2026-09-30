# [C] CVE-2026-9198

## Summary
Severity: Critical
Advisory: CVE-2026-9198
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-9198
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.0 allows unauthenticated attackers to chain /api/v1/auto_login (mints SUPERUSER tokens to any network caller) with /api/v1/validate/code (executes user code via exec()) to achieve full RCE on default Langflow deployments

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-9198
- https://www.ibm.com/support/pages/node/7278927
