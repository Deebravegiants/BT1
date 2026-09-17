# [M] CVE-2015-5247

## Summary
Severity: Medium
Advisory: CVE-2015-5247
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-14
Source: https://osv.dev/vulnerability/CVE-2015-5247
Type: osv

## Details
The virStorageVolCreateXML API in libvirt 1.2.14 through 1.2.19 allows remote authenticated users with a read-write connection to cause a denial of service (libvirtd crash) by triggering a failed unlink after creating a volume on a root_squash NFS pool.

## References
- http://security.libvirt.org/2015/0003.html
- http://www.ubuntu.com/usn/USN-2867-1
