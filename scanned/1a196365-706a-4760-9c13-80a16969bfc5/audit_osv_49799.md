# [H] CVE-2019-19079

## Summary
Severity: High
Advisory: CVE-2019-19079
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19079
Type: osv

## Details
A memory leak in the qrtr_tun_write_iter() function in net/qrtr/tun.c in the Linux kernel before 5.3 allows attackers to cause a denial of service (memory consumption), aka CID-a21b7f0cff19.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4258-1/
- https://github.com/torvalds/linux/commit/a21b7f0cff1906a93a0130b74713b15a0b36481d
