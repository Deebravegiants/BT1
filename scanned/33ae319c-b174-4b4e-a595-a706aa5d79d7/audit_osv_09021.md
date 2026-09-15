# [M] CVE-2016-7423

## Summary
Severity: Medium
Advisory: CVE-2016-7423
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2016-7423
Type: osv

## Details
The mptsas_process_scsi_io_request function in QEMU (aka Quick Emulator), when built with LSI SAS1068 Host Bus emulation support, allows local guest OS administrators to cause a denial of service (out-of-bounds write and QEMU process crash) via vectors involving MPTSASRequest objects.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=670e56d3ed2918b3861d9216f2c0540d9e9ae0d5
- http://www.openwall.com/lists/oss-security/2016/09/16/11
- http://www.openwall.com/lists/oss-security/2016/09/16/5
- http://www.securityfocus.com/bid/92997
- https://security.gentoo.org/glsa/201611-11
- https://bugzilla.redhat.com/show_bug.cgi?id=1376776
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg03604.html
