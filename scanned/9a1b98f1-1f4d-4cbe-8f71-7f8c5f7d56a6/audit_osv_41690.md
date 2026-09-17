# [C] Root RCE via image backup.yaml symlink

## Summary
Severity: Critical
Advisory: CVE-2026-63294
Aliases: GHSA-fv82-v4fj-mm4m
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63294
Type: osv

## Details
A link following vulnerability in LXD allows an attacker to achieve root command execution on the host system. During the import or unpacking of crafted image or backup archives, LXD fails to properly validate and confine the backup.yaml file when it exists as a symbolic link. An attacker can exploit this flaw by providing a malicious archive with a symlinked backup.yaml file, causing LXD to process unconfined configuration metadata and execute arbitrary commands with root privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63294.json
- https://github.com/canonical/lxd/security/advisories/GHSA-fv82-v4fj-mm4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-63294
- https://github.com/canonical/lxd
