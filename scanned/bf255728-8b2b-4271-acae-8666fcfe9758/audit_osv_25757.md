# [M] SSH key password bypassed in warpgate

## Summary
Severity: Medium
Advisory: CVE-2023-43660
Aliases: GHSA-3cjp-w4cp-m9c8
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-43660
Type: osv

## Details
Warpgate is a smart SSH, HTTPS and MySQL bastion host for Linux that doesn't need special client apps. The SSH key verification for a user can be bypassed by sending an SSH key offer without a signature. This allows bypassing authentication under following conditions: 1. The attacker knows the username and a valid target name 2. The attacked knows the user's public key and 3. Only SSH public key authentication is required for the user account. This issue has been addressed in version 0.8.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43660.json
- https://github.com/warp-tech/warpgate/security/advisories/GHSA-3cjp-w4cp-m9c8
- https://nvd.nist.gov/vuln/detail/CVE-2023-43660
- https://github.com/warp-tech/warpgate/commit/a4df7f7a21395cfaee7a9789d1e3846290caeb63
