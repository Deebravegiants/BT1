# [M] Grub2: use-after-free in grub_file_close()

## Summary
Severity: Medium
Advisory: CVE-2025-54771
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-54771
Type: osv

## Details
A use-after-free vulnerability has been identified in the GNU GRUB (Grand Unified Bootloader). The flaw occurs because the file-closing process incorrectly retains a memory pointer, leaving an invalid reference to a file system structure. An attacker could exploit this vulnerability to cause grub to crash, leading to a Denial of Service. Possible data integrity or confidentiality compromise is not discarded.

## References
- http://www.openwall.com/lists/oss-security/2025/11/18/3
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.gnu.org/archive/html/grub-devel/2025-11/msg00155.html
- https://access.redhat.com/security/cve/CVE-2025-54771
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54771.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54771
- https://bugzilla.redhat.com/show_bug.cgi?id=2413823
- https://git.savannah.gnu.org/git/grub.git
