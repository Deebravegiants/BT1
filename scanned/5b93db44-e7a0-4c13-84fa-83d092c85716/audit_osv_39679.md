# [M] Frogman: Plaintext passwords and secrets persisted to audit log

## Summary
Severity: Medium
Advisory: CVE-2026-46514
Aliases: GHSA-3p65-2prr-cfvf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46514
Type: osv

## Details
Frogman provides headless PBX control through MCP and HTTP API. Prior to 1.6.2, fm_reset_password in Tools/ResetPassword.php:48-53 returned a plaintext password and fm_add_extension in Tools/AddExtension.php:172 returned a plaintext secret; Frogman.class.php:2207-2211 used auditOutcome to JSON-encode those responses into oc_audit_log.detail, allowing any PERM_READ caller with access to fm_audit_search to recover the stored credentials. This issue is fixed in version 1.6.2.

## References
- https://github.com/mwtcmi/frogman/releases/tag/v1.6.1
- https://github.com/mwtcmi/frogman/releases/tag/v1.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46514.json
- https://github.com/mwtcmi/frogman/security/advisories/GHSA-3p65-2prr-cfvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-46514
- https://github.com/mwtcmi/frogman/commit/02203edb613774f265ad8a21d99c4f6cf7de0d4d
