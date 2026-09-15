# [H] An out-of-bounds access vulnerability involving netfilter was reported and fixed as: f1082dd31fe4 (netfilter: nf_tables: Reject tables of unsupported family)

## Summary
Severity: High
Advisory: CVE-2023-6040
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-6040
Type: osv

## Details
An out-of-bounds access vulnerability involving netfilter was reported and fixed as: f1082dd31fe4 (netfilter: nf_tables: Reject tables of unsupported family); While creating a new netfilter table, lack of a safeguard against invalid nf_tables family (pf) values within `nf_tables_newtable` function enables an attacker to achieve out-of-bounds access.

## References
- http://packetstormsecurity.com/files/177029/Kernel-Live-Patch-Security-Notice-LSN-0100-1.html
- http://www.openwall.com/lists/oss-security/2024/01/12/1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6040.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6040
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-6040
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
- https://www.openwall.com/lists/oss-security/2024/01/12/1
