# [C] CVE-2023-6816

## Summary
Severity: Critical
Advisory: CVE-2023-6816
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2023-6816
Type: osv

## Details
A flaw was found in X.Org server. Both DeviceFocusEvent and the XIQueryPointer reply contain a bit for each logical button currently down. Buttons can be arbitrarily mapped to any value up to 255, but the X.Org Server was only allocating space for the device's particular number of buttons, leading to a heap overflow if a bigger value was used.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5J4H7CH565ALSZZYKOJFYDA5KFLG6NUK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EJBMCWQ54R6ZL3MYU2D2JBW6JMZL7BQW/
- http://www.openwall.com/lists/oss-security/2024/01/18/1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IZ75X54CN4IFYMIV7OK3JVZ57FHQIGIC/
- https://security.gentoo.org/glsa/202401-30
- https://security.netapp.com/advisory/ntap-20240307-0006/
- https://access.redhat.com/errata/RHSA-2024:2996
- https://access.redhat.com/errata/RHSA-2024:0557
- https://access.redhat.com/errata/RHSA-2024:0614
- https://access.redhat.com/errata/RHSA-2024:0617
- https://access.redhat.com/errata/RHSA-2024:2170
- https://access.redhat.com/errata/RHSA-2025:12751
- https://access.redhat.com/errata/RHSA-2024:0320
- https://access.redhat.com/errata/RHSA-2024:0597
- https://access.redhat.com/errata/RHSA-2024:0607
- https://access.redhat.com/errata/RHSA-2024:0629
- https://access.redhat.com/errata/RHSA-2024:2169
- https://access.redhat.com/errata/RHSA-2024:0558
- https://access.redhat.com/errata/RHSA-2024:0621
