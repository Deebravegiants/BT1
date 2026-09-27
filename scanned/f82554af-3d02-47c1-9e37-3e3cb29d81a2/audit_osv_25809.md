# [M] Group-based JIT MFA bypass on scp and sftp in The Bastion

## Summary
Severity: Medium
Advisory: CVE-2023-45140
Aliases: GHSA-pr4q-w883-pf5x
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-11-08
Source: https://osv.dev/vulnerability/CVE-2023-45140
Type: osv

## Details
The Bastion provides authentication, authorization, traceability and auditability for SSH accesses. SCP and SFTP plugins don't honor group-based JIT MFA. Establishing a SCP/SFTP connection through The Bastion via a group access where MFA is enforced does not ask for additional factor. This abnormal behavior only applies to per-group-based JIT MFA. Other MFA setup types, such as Immediate MFA, JIT MFA on a per-plugin basis and JIT MFA on a per-account basis are not affected. This issue has been patched in version 3.14.15.

## References
- https://github.com/ovh/the-bastion/releases/tag/v3.14.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45140.json
- https://github.com/ovh/the-bastion/security/advisories/GHSA-pr4q-w883-pf5x
- https://nvd.nist.gov/vuln/detail/CVE-2023-45140
