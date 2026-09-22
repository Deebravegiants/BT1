# [M] Pimcore vulnerable to Pre-Auth Path Traversal in pimcore_log parameter

## Summary
Severity: Medium
Advisory: GHSA-46g3-f9r8-xj4v
CVE: CVE-2023-2984
CWE: CWE-29
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-46g3-f9r8-xj4v
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.22

## Details
### Impact

A path traversal vulnerability exists in the CMS, which allows an attacker to overwrite or modify sensitive files by manipulating the `pimcore_log` parameter.This can lead to potential denial of service---key file overwrite.

The impact of this vulnerability allows attackers to:

- Overwrite or modify sensitive files, potentially leading to unauthorized access, privilege escalation, or disclosure of confidential information.

- Tamper with system settings by modifying key files, such as the hosts file in Windows or configuration files for other services.

- Cause a denial of service (DoS) if critical system files are overwritten or deleted.

The consequences of exploiting this vulnerability can be detrimental to the confidentiality, integrity, and availability of the affected system. It's crucial to address this vulnerability to protect sensitive data and ensure the proper functioning of the system.

### Patches
Update to version 10.5.22 or apply this patch manually https://github.com/pimcore/pimcore/commit/e8dbc4da58ae86618bceb67ed35ce23e5e54d2ed.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/e8dbc4da58ae86618bceb67ed35ce23e5e54d2ed.patch manually.

### References
https://huntr.dev/bounties/5df8b951-e2f1-4548-a7e3-601186e1b191/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-46g3-f9r8-xj4v
- https://nvd.nist.gov/vuln/detail/CVE-2023-2984
- https://github.com/pimcore/pimcore/commit/e8dbc4da58ae86618bceb67ed35ce23e5e54d2ed
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/5df8b951-e2f1-4548-a7e3-601186e1b191
