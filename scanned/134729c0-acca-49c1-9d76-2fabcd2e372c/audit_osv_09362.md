# [M] CVE-2016-9590

## Summary
Severity: Medium
Advisory: CVE-2016-9590
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-26
Source: https://osv.dev/vulnerability/CVE-2016-9590
Type: osv

## Details
puppet-swift before versions 8.2.1, 9.4.4 is vulnerable to an information-disclosure in Red Hat OpenStack Platform director's installation of Object Storage (swift). During installation, the Puppet script responsible for deploying the service incorrectly removes and recreates the proxy-server.conf file with world-readable permissions.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0200.html
- http://rhn.redhat.com/errata/RHSA-2017-0359.html
- http://rhn.redhat.com/errata/RHSA-2017-0361.html
- http://www.securityfocus.com/bid/95448
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9590
