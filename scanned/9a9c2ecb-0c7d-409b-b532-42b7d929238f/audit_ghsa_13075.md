# [M] Pimcore Path Traversal Vulnerability in AssetController:importServerFilesAction

## Summary
Severity: Medium
Advisory: GHSA-34hj-v8fm-x887
CVE: CVE-2023-38708
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-34hj-v8fm-x887
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.6.7

## Details
### Impact
A path traversal vulnerability exists in the `AssetController::importServerFilesAction`, which allows an attacker to overwrite or modify sensitive files by manipulating the pimcore_log parameter.This can lead to potential denial of service---key file overwrite.

The impact of this vulnerability allows attackers to:

Overwrite or modify sensitive files, potentially leading to unauthorized access, privilege escalation, or disclosure of confidential information.

Tamper with system settings by modifying key files, such as the hosts file in Windows or configuration files for other services.

Cause a denial of service (DoS) if critical system files are overwritten or deleted.

The consequences of exploiting this vulnerability can be detrimental to the confidentiality, integrity, and availability of the affected system. It's crucial to address this vulnerability to protect sensitive data and ensure the proper functioning of the system.

### Patches
Update to version 10.6.7 or apply this patch manually https://github.com/pimcore/pimcore/commit/58012d0e3b8b926fb54eccbd64ec5c993b30c22c.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/58012d0e3b8b926fb54eccbd64ec5c993b30c22c.patch manually.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-34hj-v8fm-x887
- https://nvd.nist.gov/vuln/detail/CVE-2023-38708
- https://github.com/pimcore/pimcore/commit/58012d0e3b8b926fb54eccbd64ec5c993b30c22c
- https://github.com/pimcore/pimcore
