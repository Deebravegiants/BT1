# [M] CVE-2019-18808

## Summary
Severity: Medium
Advisory: CVE-2019-18808
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18808
Type: osv

## Details
A memory leak in the ccp_run_sha_cmd() function in drivers/crypto/ccp/ccp-ops.c in the Linux kernel through 5.3.9 allows attackers to cause a denial of service (memory consumption), aka CID-128c66429247.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYIFGYEDQXP5DVJQQUARQRK2PXKBKQGY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWWOOJKZ4NQYN4RMFIVJ3ZIXKJJI3MKP/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4525-1/
- https://usn.ubuntu.com/4526-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://www.openwall.com/lists/oss-security/2021/09/14/1
- https://github.com/torvalds/linux/commit/128c66429247add5128c03dc1e144ca56f05a4e2
