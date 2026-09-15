# [M] Untrusted user data can lead to privilege escalation

## Summary
Severity: Medium
Advisory: CVE-2025-6723
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/CVE-2025-6723
Type: osv

## Details
Chef InSpec versions up to 5.23 and before 7.0.107 creates named pipes with overly permissive default Windows access controls. A local attacker may interfere with the pipe connection process and exploit the insufficient access restrictions to assume the InSpec execution context, potentially resulting in elevated privileges or operational disruption.

This issue affects Chef Inspec: through 5.23 and before 7.0.107

## References
- https://docs.chef.io/inspec/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6723.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6723
- https://github.com/inspec/inspec
