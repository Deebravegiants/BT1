# [M] CVE-2018-18584

## Summary
Severity: Medium
Advisory: CVE-2018-18584
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/CVE-2018-18584
Type: osv

## Details
In mspack/cab.h in libmspack before 0.8alpha and cabextract before 1.8, the CAB block input buffer is one byte too small for the maximal Quantum block, leading to an out-of-bounds write.

## References
- https://access.redhat.com/errata/RHSA-2019:2049
- https://bugs.debian.org/911640
- https://lists.debian.org/debian-lts-announce/2018/10/msg00017.html
- https://security.gentoo.org/glsa/201903-20
- https://usn.ubuntu.com/3814-1/
- https://usn.ubuntu.com/3814-2/
- https://usn.ubuntu.com/3814-3/
- https://www.cabextract.org.uk/#changes
- https://www.openwall.com/lists/oss-security/2018/10/22/1
- https://www.starwindsoftware.com/security/sw-20181213-0001/
- https://github.com/kyz/libmspack/commit/40ef1b4093d77ad3a5cfcee1f5cb6108b3a3bcc2
