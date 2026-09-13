# [H] Dracut: dracut: root code execution via dhcp options command injection in networkmanager initrd module

## Summary
Severity: High
Advisory: CVE-2026-16445
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-16445
Type: osv

## Details
A flaw was found in dracut. A remote attacker on the adjacent network can exploit this vulnerability by providing specially crafted DHCP options, such as a malicious root-path, next-server, or bootfile name, to a system using dracut's NetworkManager-based initrd network module. These options are improperly handled and written into a temporary shell script without proper escaping, leading to command injection. This allows the attacker to achieve root code execution within the initramfs during system boot.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:26534
- https://access.redhat.com/errata/RHSA-2026:40700
- https://access.redhat.com/errata/RHSA-2026:61252
- https://access.redhat.com/security/cve/CVE-2026-16445
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16445
- https://bugzilla.redhat.com/show_bug.cgi?id=2459963
- https://bugzilla.redhat.com/show_bug.cgi?id=2503147
- https://github.com/dracutdevs/dracut/commit/e509c638e6
