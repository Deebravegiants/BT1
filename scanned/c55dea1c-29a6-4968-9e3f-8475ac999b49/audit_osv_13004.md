# [H] CVE-2018-16847

## Summary
Severity: High
Advisory: CVE-2018-16847
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-02
Source: https://osv.dev/vulnerability/CVE-2018-16847
Type: osv

## Details
An OOB heap buffer r/w access issue was found in the NVM Express Controller emulation in QEMU. It could occur in nvme_cmb_ops routines in nvme device. A guest user/process could use this flaw to crash the QEMU process resulting in DoS or potentially run arbitrary code with privileges of the QEMU process.

## References
- http://www.securityfocus.com/bid/105866
- https://usn.ubuntu.com/3826-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16847
- https://lists.gnu.org/archive/html/qemu-devel/2018-11/msg00200.html
- https://www.openwall.com/lists/oss-security/2018/11/02/1
