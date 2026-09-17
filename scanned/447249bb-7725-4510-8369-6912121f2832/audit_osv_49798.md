# [H] CVE-2019-19078

## Summary
Severity: High
Advisory: CVE-2019-19078
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19078
Type: osv

## Details
A memory leak in the ath10k_usb_hif_tx_sg() function in drivers/net/wireless/ath/ath10k/usb.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering usb_submit_urb() failures, aka CID-b8d17e7d93d2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4ISVNIC44SOGXTUBCIZFSUNQJ5LRKNZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MN6MLCN7G7VFTSXSZYXKXEFCUMFBUAXQ/
- https://usn.ubuntu.com/4287-2/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://usn.ubuntu.com/4258-1/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4287-1/
- https://github.com/torvalds/linux/commit/b8d17e7d93d2beb89e4f34c59996376b8b544792
