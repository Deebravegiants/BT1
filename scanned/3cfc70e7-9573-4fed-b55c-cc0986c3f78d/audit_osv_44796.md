# [H] Crabbox < v0.12.0 Privilege Escalation via Agent Ticket Endpoints

## Summary
Severity: High
Advisory: CVE-2026-8629
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-8629
Type: osv

## Details
Crabbox prior to v0.12.0 contains a privilege escalation vulnerability that allows users with shared visibility-only access to obtain Code, WebVNC, and Egress agent tickets by sending POST requests to ticket endpoints. Attackers can exploit insufficient access control checks on the /v1/leases/:id/code/ticket, /v1/leases/:id/webvnc/ticket, and /v1/leases/:id/egress/ticket endpoints to obtain bridge-agent tickets and impersonate trusted lease-side bridges despite having only visibility permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8629.json
- https://github.com/openclaw/crabbox/releases/tag/v0.12.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-8629
- https://www.vulncheck.com/advisories/crabbox-privilege-escalation-via-agent-ticket-endpoints
- https://github.com/openclaw/crabbox/pull/71
- https://github.com/openclaw/crabbox/commit/95cb30dc7dbaa1fef690a42ef6ac1cb6e307a191
- https://github.com/openclaw/crabbox
