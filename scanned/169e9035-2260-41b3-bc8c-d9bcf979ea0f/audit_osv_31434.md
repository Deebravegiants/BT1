# [M] Grub2: commands/dump: the dump command is not in lockdown when secure boot is enabled

## Summary
Severity: Medium
Advisory: CVE-2025-1118
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-1118
Type: osv

## Details
A flaw was found in grub2. Grub's dump command is not blocked when grub is in lockdown mode, which allows the user to read any memory information, and an attacker may leverage this in order to extract signatures, salts, and other sensitive information from the memory.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.savannah.gnu.org/cgit/grub.git/commit/?id=34824806ac6302f91e8cabaa41308eaced25725f
- https://lists.gnu.org/archive/html/grub-devel/2025-02/msg00024.html
- https://www.gnu.org/software/grub/
- https://access.redhat.com/errata/RHSA-2025:16154
- https://access.redhat.com/security/cve/CVE-2025-1118
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1118.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1118
- https://bugzilla.redhat.com/show_bug.cgi?id=2346137
