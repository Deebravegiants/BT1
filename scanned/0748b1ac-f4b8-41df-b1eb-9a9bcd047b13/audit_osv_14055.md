# [H] CVE-2018-6764

## Summary
Severity: High
Advisory: CVE-2018-6764
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-6764
Type: osv

## Details
util/virlog.c in libvirt does not properly determine the hostname on LXC container startup, which allows local guest OS users to bypass an intended container protection mechanism and execute arbitrary commands via a crafted NSS module.

## References
- http://www.ubuntu.com/usn/USN-3576-1
- https://access.redhat.com/errata/RHSA-2018:3113
- https://www.debian.org/security/2018/dsa-4137
- https://www.redhat.com/archives/libvir-list/2018-February/msg00239.html
