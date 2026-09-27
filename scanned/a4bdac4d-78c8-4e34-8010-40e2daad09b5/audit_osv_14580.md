# [H] CVE-2019-10166

## Summary
Severity: High
Advisory: CVE-2019-10166
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-10166
Type: osv

## Details
It was discovered that libvirtd, versions 4.x.x before 4.10.1 and 5.x.x before 5.4.1, would permit readonly clients to use the virDomainManagedSaveDefineXML() API, which would permit them to modify managed save state files. If a managed save had already been created by a privileged user, a local attacker could modify this file such that libvirtd would execute an arbitrary program when the domain was resumed.

## References
- https://access.redhat.com/libvirt-privesc-vulnerabilities
- https://security.gentoo.org/glsa/202003-18
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10166
