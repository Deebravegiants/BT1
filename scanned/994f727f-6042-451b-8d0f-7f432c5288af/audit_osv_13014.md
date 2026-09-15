# [H] CVE-2018-16867

## Summary
Severity: High
Advisory: CVE-2018-16867
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-12
Source: https://osv.dev/vulnerability/CVE-2018-16867
Type: osv

## Details
A flaw was found in qemu Media Transfer Protocol (MTP) before version 3.1.0. A path traversal in the in usb_mtp_write_data function in hw/usb/dev-mtp.c due to an improper filename sanitization. When the guest device is mounted in read-write mode, this allows to read/write arbitrary files which may lead do DoS scenario OR possibly lead to code execution on the host.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CGCFIFSIWUREEQQOZDZFBYKWZHXCWBZN/
- http://www.securityfocus.com/bid/106195
- https://usn.ubuntu.com/3923-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16867
- https://www.openwall.com/lists/oss-security/2018/12/06/1
