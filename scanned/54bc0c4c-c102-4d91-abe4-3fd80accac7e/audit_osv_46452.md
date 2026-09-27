# [C] CVE-2011-1930

## Summary
Severity: Critical
Advisory: CVE-2011-1930
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-14
Source: https://osv.dev/vulnerability/CVE-2011-1930
Type: osv

## Details
In klibc 1.5.20 and 1.5.21, the DHCP options written by ipconfig to /tmp/net-$DEVICE.conf are not properly escaped. This may allow a remote attacker to send a specially crafted DHCP reply which could execute arbitrary code with the privileges of any process which sources DHCP options.

## References
- http://security.gentoo.org/glsa/glsa-201309-21.xml
- http://www.openwall.com/lists/oss-security/2012/05/22/12
- http://www.securityfocus.com/bid/47924
- https://access.redhat.com/security/cve/cve-2011-1930
- https://security-tracker.debian.org/tracker/CVE-2011-1930
- http://www.openwall.com/lists/oss-security/2012/05/22/12
- https://access.redhat.com/security/cve/cve-2011-1930
