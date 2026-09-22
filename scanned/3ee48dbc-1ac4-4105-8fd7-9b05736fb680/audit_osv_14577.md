# [H] CVE-2019-10161

## Summary
Severity: High
Advisory: CVE-2019-10161
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-10161
Type: osv

## Details
It was discovered that libvirtd before versions 4.10.1 and 5.4.1 would permit read-only clients to use the virDomainSaveImageGetXMLDesc() API, specifying an arbitrary path which would be accessed with the permissions of the libvirtd process. An attacker with access to the libvirtd socket could use this to probe the existence of arbitrary files, cause denial of service or cause libvirtd to execute arbitrary programs.

## References
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=aed6a032cead4386472afb24b16196579e239580
- https://access.redhat.com/libvirt-privesc-vulnerabilities
- https://security.gentoo.org/glsa/202003-18
- https://usn.ubuntu.com/4047-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10161
