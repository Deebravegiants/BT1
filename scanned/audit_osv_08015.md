# [H] CVE-2016-10012

## Summary
Severity: High
Advisory: CVE-2016-10012
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-05
Source: https://osv.dev/vulnerability/CVE-2016-10012
Type: osv

## Details
The shared memory manager (associated with pre-authentication compression) in sshd in OpenSSH before 7.4 does not ensure that a bounds check is enforced by all compilers, which might allows local users to gain privileges by leveraging access to a sandboxed privilege-separation process, related to the m_zback and m_zlib data structures.

## References
- http://www.securityfocus.com/bid/94975
- http://www.securitytracker.com/id/1037490
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.647637
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://support.f5.com/csp/article/K62201745?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03818en_us
- https://www.openssh.com/txt/release-7.4
- http://www.openwall.com/lists/oss-security/2016/12/19/2
- https://access.redhat.com/errata/RHSA-2017:2029
- https://security.netapp.com/advisory/ntap-20171130-0002/
- https://github.com/openbsd/src/commit/3095060f479b86288e31c79ecbc5131a66bcd2f9
