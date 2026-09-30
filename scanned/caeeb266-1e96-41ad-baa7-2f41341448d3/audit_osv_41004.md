# [M] NanoClaw < 2.1.17 - Privilege Escalation via Unauthorized create_agent System Action

## Summary
Severity: Medium
Advisory: CVE-2026-56693
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56693
Type: osv

## Details
NanoClaw before 2.1.17 contains a privilege escalation vulnerability in the create_agent delivery-action handler that performs privileged central-database writes without host-side authorization checks. Confined agent containers can invoke create_agent to create arbitrary agent groups, container configurations, and destinations, escalating beyond their intended confinement boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56693.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56693
- https://www.vulncheck.com/advisories/nanoclaw-privilege-escalation-via-unauthorized-create-agent-system-action
- https://github.com/nanocoai/nanoclaw/pull/2720
- https://github.com/nanocoai/nanoclaw/commit/ac37ecbfd6b9d14fdfa1598a6412a8ffdbeaef45
- https://github.com/nanocoai/nanoclaw
