# [M] CVE-2016-6210

## Summary
Severity: Medium
Advisory: CVE-2016-6210
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-6210
Type: osv

## Details
sshd in OpenSSH before 7.3, when SHA256 or SHA512 are used for user password hashing, uses BLOWFISH hashing on a static password when the username does not exist, which allows remote attackers to enumerate users by leveraging the timing difference between responses when a large password is provided.

## References
- http://www.securitytracker.com/id/1036319
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://www.exploit-db.com/exploits/40113/
- https://www.exploit-db.com/exploits/40136/
- http://seclists.org/fulldisclosure/2016/Jul/51
- http://www.debian.org/security/2016/dsa-3626
- http://www.securityfocus.com/bid/91812
- https://access.redhat.com/errata/RHSA-2017:2029
- https://access.redhat.com/errata/RHSA-2017:2563
- https://security.gentoo.org/glsa/201612-18
- https://security.netapp.com/advisory/ntap-20190206-0001/
- https://www.openssh.com/txt/release-7.3
