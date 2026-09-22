# [H] CVE-2019-18812

## Summary
Severity: High
Advisory: CVE-2019-18812
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18812
Type: osv

## Details
A memory leak in the sof_dfsentry_write() function in sound/soc/sof/debug.c in the Linux kernel through 5.3.9 allows attackers to cause a denial of service (memory consumption), aka CID-c0a333d842ef.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LYIFGYEDQXP5DVJQQUARQRK2PXKBKQGY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWWOOJKZ4NQYN4RMFIVJ3ZIXKJJI3MKP/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/torvalds/linux/commit/c0a333d842ef67ac04adc72ff79dc1ccc3dca4ed
