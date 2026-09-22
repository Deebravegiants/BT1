# [H] CVE-2019-10167

## Summary
Severity: High
Advisory: CVE-2019-10167
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-10167
Type: osv

## Details
The virConnectGetDomainCapabilities() libvirt API, versions 4.x.x before 4.10.1 and 5.x.x before 5.4.1, accepts an "emulatorbin" argument to specify the program providing emulation for a domain. Since v1.2.19, libvirt will execute that program to probe the domain's capabilities. Read-only clients could specify an arbitrary path for this argument, causing libvirtd to execute a crafted executable with its own privileges.

## References
- https://access.redhat.com/libvirt-privesc-vulnerabilities
- https://security.gentoo.org/glsa/202003-18
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10167
