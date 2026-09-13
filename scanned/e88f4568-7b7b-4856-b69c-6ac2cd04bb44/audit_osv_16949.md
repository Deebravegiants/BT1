# [M] CVE-2020-10807

## Summary
Severity: Medium
Advisory: CVE-2020-10807
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-03-22
Source: https://osv.dev/vulnerability/CVE-2020-10807
Type: osv

## Details
auth_svc in Caldera before 2.6.5 allows authentication bypass (for REST API requests) via a forged "localhost" string in the HTTP Host header.

## References
- https://github.com/mitre/caldera/compare/2.6.4...2.6.5
- https://github.com/mitre/caldera/issues/1405
- https://github.com/mitre/caldera/releases/tag/2.6.5
- https://github.com/mitre/caldera/pull/1407
