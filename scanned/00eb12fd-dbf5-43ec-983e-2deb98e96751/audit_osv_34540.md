# [M] Grub2: grub2: out-of-bounds write via malicious usb device

## Summary
Severity: Medium
Advisory: CVE-2025-61661
CVSS: 4.8 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-61661
Type: osv

## Details
A vulnerability has been identified in the GRUB (Grand Unified Bootloader) component. This flaw occurs because the bootloader mishandles string conversion when reading information from a USB device, allowing an attacker to exploit inconsistent length values. A local attacker can connect a maliciously configured USB device during the boot sequence to trigger this issue. A successful exploitation may lead GRUB to crash, leading to a Denial of Service. Data corruption may be also possible, although given the complexity of the exploit the impact is most likely limited.

## References
- http://www.openwall.com/lists/oss-security/2025/11/18/8
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-61661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61661.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61661
- https://bugzilla.redhat.com/show_bug.cgi?id=2413827
- https://git.savannah.gnu.org/git/grub.git
