# [H] CVE-2023-1118

## Summary
Severity: High
Advisory: CVE-2023-1118
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-02
Source: https://osv.dev/vulnerability/CVE-2023-1118
Type: osv

## Details
A flaw use after free in the Linux kernel integrated infrared receiver/transceiver driver was found in the way user detaching rc device. A local user could use this flaw to crash the system or potentially escalate their privileges on the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1118.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1118
- https://security.netapp.com/advisory/ntap-20230413-0003/
- https://github.com/torvalds/linux/commit/29b0589a865b6f66d141d79b2dd1373e4e50fe17
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
