# [M] CVE-2019-19076

## Summary
Severity: Medium
Advisory: CVE-2019-19076
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19076
Type: osv

## Details
A memory leak in the nfp_abm_u32_knode_replace() function in drivers/net/ethernet/netronome/nfp/abm/cls.c in the Linux kernel before 5.3.6 allows attackers to cause a denial of service (memory consumption), aka CID-78beef629fd9. NOTE: This has been argued as not a valid vulnerability. The upstream commit 78beef629fd9 was reverted

## References
- https://lore.kernel.org/lkml/20191204103955.63c4d9af%40cakuba.netronome.com/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4209-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.6
- https://git.kernel.org/linus/1d1997db870f4058676439ef7014390ba9e24eb2
- https://github.com/torvalds/linux/commit/78beef629fd95be4ed853b2d37b832f766bd96ca
