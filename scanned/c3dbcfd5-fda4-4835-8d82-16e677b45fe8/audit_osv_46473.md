# [M] CVE-2011-4600

## Summary
Severity: Medium
Advisory: CVE-2011-4600
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-04-14
Source: https://osv.dev/vulnerability/CVE-2011-4600
Type: osv

## Details
The networkReloadIptablesRules function in network/bridge_driver.c in libvirt before 0.9.9 does not properly handle firewall rules on bridge networks when libvirtd is restarted, which might allow remote attackers to bypass intended access restrictions via a (1) DNS or (2) DHCP query.

## References
- http://libvirt.org/news-2012.html
- http://www.ubuntu.com/usn/USN-2867-1
- https://bugzilla.redhat.com/show_bug.cgi?id=760442
- http://libvirt.org/git/?p=libvirt.git%3Ba=commitdiff%3Bh=ae1232b298323dd7bef909426e2ebafa6bca9157
