# [M] Libx11: stack exhaustion from infinite recursion in putsubimage()

## Summary
Severity: Medium
Advisory: CVE-2023-43786
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/CVE-2023-43786
Type: osv

## Details
A vulnerability was found in libX11 due to an infinite loop within the PutSubImage() function. This flaw allows a local user to consume all available system resources and cause a denial of service condition.

## References
- http://www.openwall.com/lists/oss-security/2024/01/24/9
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/63IBRFLQVZSMOAZBZOBKFWJP26ILRAGQ/
- https://access.redhat.com/errata/RHSA-2024:2145
- https://access.redhat.com/errata/RHSA-2024:2973
- https://access.redhat.com/security/cve/CVE-2023-43786
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43786.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43786
- https://security.netapp.com/advisory/ntap-20231103-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2242253
- https://gitlab.freedesktop.org/xorg/lib/libxpm
