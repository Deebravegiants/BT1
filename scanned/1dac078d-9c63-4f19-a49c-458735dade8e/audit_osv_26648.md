# [H] Use-after-free in Linux kernel's fs/smb/client component

## Summary
Severity: High
Advisory: CVE-2023-5345
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-5345
Type: osv

## Details
A use-after-free vulnerability in the Linux kernel's fs/smb/client component can be exploited to achieve local privilege escalation.

In case of an error in smb3_fs_context_parse_param, ctx->password was freed but the field was not set to NULL which could lead to double free.

We recommend upgrading past commit e6e43b8aa7cd3c3af686caf0c2e11819a886d705.

## References
- http://packetstormsecurity.com/files/177029/Kernel-Live-Patch-Security-Notice-LSN-0100-1.html
- https://git.kernel.org
- https://kernel.dance/e6e43b8aa7cd3c3af686caf0c2e11819a886d705
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GISYSL3F6WIEVGHJGLC2MFNTUXHPTKQH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GPMICQ2HVZO5UAM5KPXHAZKA2U3ZDOO6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V5PDNWPKAP3WL5RQZ4RIDS6MG32OHH5R/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5345.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5345
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e6e43b8aa7cd3c3af686caf0c2e11819a886d705
