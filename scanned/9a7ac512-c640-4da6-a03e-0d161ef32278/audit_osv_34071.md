# [M] Sandboxie exposes encrypted sandbox key during password change

## Summary
Severity: Medium
Advisory: CVE-2025-54422
Aliases: GHSA-jp7r-vgv9-43p7
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-29
Source: https://osv.dev/vulnerability/CVE-2025-54422
Type: osv

## Details
Sandboxie is a sandbox-based isolation software for 32-bit and 64-bit Windows NT-based operating systems. In versions 1.16.1 and below, a critical security vulnerability exists in password handling mechanisms. During encrypted sandbox creation, user passwords are transmitted via shared memory, exposing them to potential interception. The vulnerability is particularly severe during password modification operations, where both old and new passwords are passed as plaintext command-line arguments to the Imbox process without any encryption or obfuscation. This implementation flaw allows any process within the user session, including unprivileged processes, to retrieve these sensitive credentials by reading the command-line arguments, thereby bypassing standard privilege requirements and creating a significant security risk. This is fixed in version 1.16.2.

## References
- https://github.com/sandboxie-plus/Sandboxie/releases/tag/v1.16.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54422.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-jp7r-vgv9-43p7
- https://nvd.nist.gov/vuln/detail/CVE-2025-54422
- https://github.com/sandboxie-plus/Sandboxie/commit/d107d5743880da28e782c1771b5246b2a512989a
