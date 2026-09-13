# [H] CVE-2023-3268

## Summary
Severity: High
Advisory: CVE-2023-3268
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-3268
Type: osv

## Details
An out of bounds (OOB) memory access flaw was found in the Linux kernel in relay_file_read_start_pos in kernel/relay.c in the relayfs. This flaw could allow a local attacker to crash the system or leak kernel internal information.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=43ec16f1450f4936025a9bdf1a273affdb9732c1
- https://lore.kernel.org/lkml/1682238502-1892-1-git-send-email-yangpc%40wangsu.com/T/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3268.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3268
- https://security.netapp.com/advisory/ntap-20230824-0006/
- https://www.debian.org/security/2023/dsa-5448
- https://www.debian.org/security/2023/dsa-5480
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
