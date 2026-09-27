# [M] Grub2: use-after-free in net_set_vlan

## Summary
Severity: Medium
Advisory: CVE-2025-54770
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-54770
Type: osv

## Details
A vulnerability has been identified in the GRUB2 bootloader's network module that poses an immediate Denial of Service (DoS) risk. This flaw is a Use-after-Free issue, caused because the net_set_vlan command is not properly unregistered when the network module is unloaded from memory. An attacker who can execute this command can force the system to access memory locations that are no longer valid. Successful exploitation leads directly to system instability, which can result in a complete crash and halt system availability

## References
- http://www.openwall.com/lists/oss-security/2025/11/18/4
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.gnu.org/archive/html/grub-devel/2025-11/msg00155.html
- https://access.redhat.com/security/cve/CVE-2025-54770
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54770.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54770
- https://bugzilla.redhat.com/show_bug.cgi?id=2413813
- https://git.savannah.gnu.org/git/grub.git
