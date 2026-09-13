# [H] CVE-2015-8325

## Summary
Severity: High
Advisory: CVE-2015-8325
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-01
Source: https://osv.dev/vulnerability/CVE-2015-8325
Type: osv

## Details
The do_setup_env function in session.c in sshd in OpenSSH through 7.2p2, when the UseLogin feature is enabled and PAM is configured to read .pam_environment files in user home directories, allows local users to gain privileges by triggering a crafted environment for the /bin/login program, as demonstrated by an LD_PRELOAD environment variable.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2588.html
- http://rhn.redhat.com/errata/RHSA-2017-0641.html
- http://www.debian.org/security/2016/dsa-3550
- https://security.gentoo.org/glsa/201612-18
- https://security.netapp.com/advisory/ntap-20180628-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1328012
- http://www.securityfocus.com/bid/86187
- http://www.securitytracker.com/id/1036487
- https://anongit.mindrot.org/openssh.git/commit/?id=85bdcd7c92fe7ff133bbc4e10a65c91810f88755
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://people.canonical.com/~ubuntu-security/cve/2015/CVE-2015-8325.html
- https://security-tracker.debian.org/tracker/CVE-2015-8325
