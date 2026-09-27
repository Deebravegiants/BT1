# [M] Migration-planner: credentialurl validator accepts javascript: urls

## Summary
Severity: Medium
Advisory: CVE-2026-53472
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-53472
Type: osv

## Details
A flaw was found in migration-planner. Insufficient validation of the `AgentStatusUpdate.CredentialUrl` field allows an authenticated attacker to store a malicious `javascript:` URL. When a victim views this URL in the Hybrid Cloud Console, it can lead to Cross-Site Scripting (XSS), enabling script execution in the victim's session and potentially disclosing sensitive information.

## References
- https://access.redhat.com/security/cve/CVE-2026-53472
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53472.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53472
- https://bugzilla.redhat.com/show_bug.cgi?id=2487073
- https://github.com/kubev2v/migration-planner
