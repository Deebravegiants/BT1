# [H] Xorg-x11-server: heap buffer overflow in xisenddevicehierarchyevent

## Summary
Severity: High
Advisory: CVE-2024-21885
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-21885
Type: osv

## Details
A flaw was found in X.Org server. In the XISendDeviceHierarchyEvent function, it is possible to exceed the allocated array length when certain new device IDs are added to the xXIHierarchyInfo struct. This can trigger a heap buffer overflow condition, which may lead to an application crash or remote code execution in SSH X11 forwarding environments.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/01/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5J4H7CH565ALSZZYKOJFYDA5KFLG6NUK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EJBMCWQ54R6ZL3MYU2D2JBW6JMZL7BQW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IZ75X54CN4IFYMIV7OK3JVZ57FHQIGIC/
- https://access.redhat.com/errata/RHSA-2024:0320
- https://access.redhat.com/errata/RHSA-2024:0557
- https://access.redhat.com/errata/RHSA-2024:0558
- https://access.redhat.com/errata/RHSA-2024:0597
- https://access.redhat.com/errata/RHSA-2024:0607
- https://access.redhat.com/errata/RHSA-2024:0614
- https://access.redhat.com/errata/RHSA-2024:0617
- https://access.redhat.com/errata/RHSA-2024:0621
- https://access.redhat.com/errata/RHSA-2024:0626
- https://access.redhat.com/errata/RHSA-2024:0629
- https://access.redhat.com/errata/RHSA-2024:2169
- https://access.redhat.com/errata/RHSA-2024:2170
- https://access.redhat.com/errata/RHSA-2024:2995
- https://access.redhat.com/errata/RHSA-2024:2996
- https://access.redhat.com/errata/RHSA-2025:12751
