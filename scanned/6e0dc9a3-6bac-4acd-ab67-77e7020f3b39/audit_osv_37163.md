# [M] U-Boot < 2026.07-rc2 Buffer Overflow in nfs_readlink_reply() via NFS READLINK

## Summary
Severity: Medium
Advisory: CVE-2026-29009
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-29009
Type: osv

## Details
U-Boot before 2026.07-rc2 contains a buffer overflow vulnerability in nfs_readlink_reply() (net/nfs-common.c) when CONFIG_CMD_NFS is enabled, allowing a malicious or compromised NFS server to overflow the 2048-byte nfs_path_buff buffer by returning multiple relative symlink targets that are appended without cumulative length validation. Attackers can send two or more READLINK responses containing relative symlink targets of approximately 1100 bytes each to corrupt adjacent BSS variables including nfs_server_ip, nfs_server_mount_port, nfs_server_port, nfs_our_port, nfs_state, and rpc_id, potentially achieving memory corruption and control over the NFS client state machine.

## References
- https://u-boot.org/
- https://git.u-boot-project.org/u-boot/u-boot/-/releases/v2026.07-rc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29009.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29009
- https://www.vulncheck.com/advisories/u-boot-rc3-buffer-overflow-in-nfs-readlink-reply-via-nfs-readlink
- https://lists.denx.de/pipermail/u-boot/2026-May/617853.html
- https://git.u-boot-project.org/u-boot/u-boot/-/commit/d6694018eaddefac6aae974f9cec72fd6e58f1bc
- https://github.com/u-boot/u-boot
- https://y637f9qq2x.com/posts/u-boot-tcp-nfs-vulns/
