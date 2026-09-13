# [M] CVE-2017-2635

## Summary
Severity: Medium
Advisory: CVE-2017-2635
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2017-2635
Type: osv

## Details
A NULL pointer deference flaw was found in the way libvirt from 2.5.0 to 3.0.0 handled empty drives. A remote authenticated attacker could use this flaw to crash libvirtd daemon resulting in denial of service.

## References
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=c3de387380f6057ee0e46cd9f2f0a092e8070875
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2635
