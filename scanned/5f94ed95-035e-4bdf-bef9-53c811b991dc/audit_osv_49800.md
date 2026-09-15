# [M] CVE-2019-19080

## Summary
Severity: Medium
Advisory: CVE-2019-19080
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19080
Type: osv

## Details
Four memory leaks in the nfp_flower_spawn_phy_reprs() function in drivers/net/ethernet/netronome/nfp/flower/main.c in the Linux kernel before 5.3.4 allow attackers to cause a denial of service (memory consumption), aka CID-8572cea1461a.

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.4
- https://github.com/torvalds/linux/commit/8572cea1461a006bce1d06c0c4b0575869125fa4
