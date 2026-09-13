# [C] CVE-2009-3616

## Summary
Severity: Critical
Advisory: CVE-2009-3616
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2009-10-23
Source: https://osv.dev/vulnerability/CVE-2009-3616
Type: osv

## Details
Multiple use-after-free vulnerabilities in vnc.c in the VNC server in QEMU 0.10.6 and earlier might allow guest OS users to execute arbitrary code on the host OS by establishing a connection from a VNC client and then (1) disconnecting during data transfer, (2) sending a message using incorrect integer data types, or (3) using the Fuzzy Screen Mode protocol, related to double free vulnerabilities.

## References
- http://rhn.redhat.com/errata/RHEA-2009-1272.html
- http://www.securityfocus.com/bid/36716
- http://marc.info/?l=qemu-devel&m=124324043812915
- http://www.openwall.com/lists/oss-security/2009/10/16/5
- http://www.openwall.com/lists/oss-security/2009/10/16/8
- http://git.savannah.gnu.org/cgit/qemu.git/commit/?id=198a0039c5
- http://git.savannah.gnu.org/cgit/qemu.git/commit/?id=753b405331
- https://bugzilla.redhat.com/show_bug.cgi?id=505641
- http://www.openwall.com/lists/oss-security/2009/10/16/5
- http://www.openwall.com/lists/oss-security/2009/10/16/8
- https://bugzilla.redhat.com/show_bug.cgi?id=501131
- https://bugzilla.redhat.com/show_bug.cgi?id=501131
- https://bugzilla.redhat.com/show_bug.cgi?id=505641
- https://bugzilla.redhat.com/show_bug.cgi?id=508567
- http://git.savannah.gnu.org/cgit/qemu.git/commit/?id=198a0039c5
- http://git.savannah.gnu.org/cgit/qemu.git/commit/?id=753b405331
- http://www.securityfocus.com/bid/36716
