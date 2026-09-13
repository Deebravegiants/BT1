# [M] CVE-2017-14489

## Summary
Severity: Medium
Advisory: CVE-2017-14489
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-15
Source: https://osv.dev/vulnerability/CVE-2017-14489
Type: osv

## Details
The iscsi_if_rx function in drivers/scsi/scsi_transport_iscsi.c in the Linux kernel through 4.13.2 allows local users to cause a denial of service (panic) by leveraging incorrect length validation.

## References
- https://usn.ubuntu.com/3583-2/
- https://www.exploit-db.com/exploits/42932/
- http://www.securityfocus.com/bid/101011
- https://usn.ubuntu.com/3583-1/
- http://www.debian.org/security/2017/dsa-3981
- https://bugzilla.redhat.com/show_bug.cgi?id=1490421
- https://patchwork.kernel.org/patch/9923803/
