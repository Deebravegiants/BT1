# [H] CVE-2016-3710

## Summary
Severity: High
Advisory: CVE-2016-3710
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-05-11
Source: https://osv.dev/vulnerability/CVE-2016-3710
Type: osv

## Details
The VGA module in QEMU improperly performs bounds checking on banked access to video memory, which allows local guest OS administrators to execute arbitrary code on the host by changing access modes after setting the bank register, aka the "Dark Portal" issue.

## References
- http://rhn.redhat.com/errata/RHSA-2016-0724.html
- http://rhn.redhat.com/errata/RHSA-2016-0725.html
- http://rhn.redhat.com/errata/RHSA-2016-0997.html
- http://rhn.redhat.com/errata/RHSA-2016-0999.html
- http://rhn.redhat.com/errata/RHSA-2016-1000.html
- http://rhn.redhat.com/errata/RHSA-2016-1001.html
- http://rhn.redhat.com/errata/RHSA-2016-1002.html
- http://rhn.redhat.com/errata/RHSA-2016-1019.html
- http://rhn.redhat.com/errata/RHSA-2016-1943.html
- http://support.citrix.com/article/CTX212736
- http://www.debian.org/security/2016/dsa-3573
- http://www.openwall.com/lists/oss-security/2016/05/09/3
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/90316
- http://www.securitytracker.com/id/1035794
- http://www.ubuntu.com/usn/USN-2974-1
- http://xenbits.xen.org/xsa/advisory-179.html
- https://access.redhat.com/errata/RHSA-2016:1224
