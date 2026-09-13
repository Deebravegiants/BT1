# [C] OpenZiti - Privilege Escalation to Admin via Unauthorized Enrollment Creation

## Summary
Severity: Critical
Advisory: CVE-2026-58165
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58165
Type: osv

## Details
OpenZiti through 2.0.0, fixed in commit 3027fdf, contains a privilege escalation vulnerability that allows authenticated non-admin identities with fine-grained enrollment management permissions to create enrollments for any identity, including the default administrator, because the ApplyCreate function in controller/model/enrollment_manager.go verifies only that the target identity exists without performing authorization checks binding the caller to the target identity. Attackers can redeem the resulting one-time token through the unauthenticated client API enrollment endpoint to obtain a client certificate authenticating as the targeted admin identity, yielding full administrative control of the controller and the zero-trust overlay it manages.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58165.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58165
- https://www.vulncheck.com/advisories/openziti-privilege-escalation-to-admin-via-unauthorized-enrollment-creation
- https://github.com/openziti/ziti/pull/4013
- https://github.com/openziti/ziti/commit/3027fdffd3e57884487b7c46e5e669cfbc8becdf
- https://github.com/openziti/ziti
- https://github.com/openziti/ziti/issues/4010
