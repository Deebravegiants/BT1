# [H] CVE-2018-1061

## Summary
Severity: High
Advisory: CVE-2018-1061
Aliases: PSF-2018-4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-1061
Type: osv

## Details
python before versions 2.7.15, 3.4.9, 3.5.6rc1, 3.6.5rc1 and 3.7.0 is vulnerable to catastrophic backtracking in the difflib.IS_LINE_JUNK method.  An attacker could use this flaw to cause denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/46PVWY5LFP4BRPG3BVQ5QEEFYBVEXHCK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AEZ5IQT7OF7Q2NCGIVABOWYGKO7YU3NJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JSKPGPZQNTAULHW4UH63KGOOUIDE4RRB/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbst03951en_us
- http://www.securitytracker.com/id/1042001
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3041
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2019:1260
- https://access.redhat.com/errata/RHSA-2019:3725
- https://bugs.python.org/issue32981
- https://docs.python.org/3.5/whatsnew/changelog.html#python-3-5-6-release-candidate-1
- https://docs.python.org/3.6/whatsnew/changelog.html#python-3-6-5-release-candidate-1
- https://lists.debian.org/debian-lts-announce/2018/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00031.html
- https://usn.ubuntu.com/3817-1/
- https://usn.ubuntu.com/3817-2/
- https://www.debian.org/security/2018/dsa-4306
- https://www.debian.org/security/2018/dsa-4307
