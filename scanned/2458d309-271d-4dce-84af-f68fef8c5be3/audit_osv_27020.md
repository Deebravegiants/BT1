# [M] Xorg-x11-server: selinux unlabeled glx pbuffer

## Summary
Severity: Medium
Advisory: CVE-2024-0408
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2024-0408
Type: osv

## Details
A flaw was found in the X.Org server. The GLX PBuffer code does not call the XACE hook when creating the buffer, leaving it unlabeled. When the client issues another request to access that resource (as with a GetGeometry) or when it creates another resource that needs to access that buffer, such as a GC, the XSELINUX code will try to use an object that was never labeled and crash because the SID is NULL.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/01/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5J4H7CH565ALSZZYKOJFYDA5KFLG6NUK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EJBMCWQ54R6ZL3MYU2D2JBW6JMZL7BQW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IZ75X54CN4IFYMIV7OK3JVZ57FHQIGIC/
- https://access.redhat.com/errata/RHSA-2024:0320
- https://access.redhat.com/errata/RHSA-2024:2169
- https://access.redhat.com/errata/RHSA-2024:2170
- https://access.redhat.com/errata/RHSA-2024:2995
- https://access.redhat.com/errata/RHSA-2024:2996
- https://access.redhat.com/security/cve/CVE-2024-0408
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0408.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0408
- https://security.gentoo.org/glsa/202401-30
- https://security.netapp.com/advisory/ntap-20240307-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2257689
- https://gitlab.freedesktop.org/xorg/xserver
