# [M] Libxpm: out of bounds read in xpmcreatexpmimagefrombuffer()

## Summary
Severity: Medium
Advisory: CVE-2023-43788
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/CVE-2023-43788
Type: osv

## Details
A vulnerability was found in libXpm due to a boundary condition within the XpmCreateXpmImageFromBuffer() function. This flaw allows a local attacker to trigger an out-of-bounds read error and read the contents of memory on the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/63IBRFLQVZSMOAZBZOBKFWJP26ILRAGQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I3KFUQT42R7TB4D7RISNSBQFJGLTQGUL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TFAJTBNO3PAIA6EGZR4PN62H6RLKNDTE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V6FARGWN7VWXXWPXYNEEDJLRR3EWFZ3T/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZECBCLDYUGLDSVV75ECPIBW7JXOB3747/
- https://access.redhat.com/errata/RHSA-2024:2146
- https://access.redhat.com/errata/RHSA-2024:2217
- https://access.redhat.com/errata/RHSA-2024:2974
- https://access.redhat.com/errata/RHSA-2024:3022
- https://access.redhat.com/security/cve/CVE-2023-43788
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43788.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43788
- https://bugzilla.redhat.com/show_bug.cgi?id=2242248
- https://gitlab.freedesktop.org/xorg/lib/libxpm
