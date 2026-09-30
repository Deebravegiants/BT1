# [M] NanoClaw < 2.1.17 - Privilege Escalation via Unverified Approval Response Handler

## Summary
Severity: Medium
Advisory: CVE-2026-56402
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56402
Type: osv

## Details
NanoClaw before 2.1.17 contains a privilege escalation vulnerability in the handleApprovalsResponse function that fails to verify responder role authorization. Attackers with a valid questionId can approve or reject privileged actions like package installation by submitting approval response payloads without proper role validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56402.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56402
- https://www.vulncheck.com/advisories/nanoclaw-privilege-escalation-via-unverified-approval-response-handler
- https://github.com/nanocoai/nanoclaw/pull/2478
- https://github.com/nanocoai/nanoclaw/commit/6227bd1a5b016fb1eb76411bb6681b4c924a51a0
- https://github.com/nanocoai/nanoclaw
