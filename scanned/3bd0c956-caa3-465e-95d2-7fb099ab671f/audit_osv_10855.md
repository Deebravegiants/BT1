# [M] CVE-2017-3265

## Summary
Severity: Medium
Advisory: CVE-2017-3265
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2017-3265
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Packaging). Supported versions that are affected are 5.5.53 and earlier, 5.6.34 and earlier and 5.7.16 and earlier. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all MySQL Server accessible data and unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS v3.0 Base Score 5.6 (Confidentiality and Availability impacts).

## References
- http://www.debian.org/security/2017/dsa-3767
- http://www.debian.org/security/2017/dsa-3770
- http://www.securityfocus.com/bid/95520
- http://www.securitytracker.com/id/1037640
- https://access.redhat.com/errata/RHSA-2017:2192
- https://access.redhat.com/errata/RHSA-2017:2787
- https://access.redhat.com/errata/RHSA-2018:0279
- https://access.redhat.com/errata/RHSA-2018:0574
- https://security.gentoo.org/glsa/201702-17
- https://security.gentoo.org/glsa/201702-18
- http://www.oracle.com/technetwork/security-advisory/cpujan2017-2881727.html
