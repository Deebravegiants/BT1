# [M] CVE-2023-3159

## Summary
Severity: Medium
Advisory: CVE-2023-3159
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-12
Source: https://osv.dev/vulnerability/CVE-2023-3159
Type: osv

## Details
A use after free issue was discovered in driver/firewire in outbound_phy_packet_callback in the Linux Kernel. In this flaw a local attacker with special privilege may cause a use after free problem when queue_event() fails.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3159.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3159
- https://github.com/torvalds/linux/commit/b7c81f80246fac44077166f3e07103affe6db8ff
