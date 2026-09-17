# [M] Grub2: missing unregister call for normal commands may lead to use-after-free

## Summary
Severity: Medium
Advisory: CVE-2025-61663
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-61663
Type: osv

## Details
A vulnerability has been identified in the GRUB2 bootloader's normal command that poses an immediate Denial of Service (DoS) risk. This flaw is a Use-after-Free issue, caused because the normal command is not properly unregistered when the module is unloaded. An attacker who can execute this command can force the system to access memory locations that are no longer valid. Successful exploitation leads directly to system instability, which can result in a complete crash and halt system availability. Impact on the data integrity and confidentiality is also not discarded.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-61663
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61663.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61663
- https://bugzilla.redhat.com/show_bug.cgi?id=2414684
- https://git.savannah.gnu.org/git/grub.git
