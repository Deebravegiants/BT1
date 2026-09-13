# [M] CVE-2024-34397

## Summary
Severity: Medium
Advisory: CVE-2024-34397
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/CVE-2024-34397
Type: osv

## Details
An issue was discovered in GNOME GLib before 2.78.5, and 2.79.x and 2.80.x before 2.80.1. When a GDBus-based client subscribes to signals from a trusted system service such as NetworkManager on a shared computer, other users of the same computer can send spoofed D-Bus signals that the GDBus-based client will wrongly interpret as having been sent by the trusted system service. This could lead to the GDBus-based client behaving incorrectly, with an application-dependent impact.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IRSFYAE5X23TNRWX7ZWEJOMISLCDSYNS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LCDY3KA7G7D3DRXYTT46K6LFHS2KHWBH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LL6HSJDXCXMLEIJBYV6CPOR4K2NTCTXW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UNFJHISR4O6VFOHBFWH5I5WWMG37H63A/
- https://www.openwall.com/lists/oss-security/2024/05/07/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34397.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IRSFYAE5X23TNRWX7ZWEJOMISLCDSYNS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LCDY3KA7G7D3DRXYTT46K6LFHS2KHWBH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LL6HSJDXCXMLEIJBYV6CPOR4K2NTCTXW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UNFJHISR4O6VFOHBFWH5I5WWMG37H63A/
- https://nvd.nist.gov/vuln/detail/CVE-2024-34397
- https://security.netapp.com/advisory/ntap-20240531-0008/
- https://gitlab.gnome.org/GNOME/glib/-/issues/3268
- https://lists.debian.org/debian-lts-announce/2024/05/msg00008.html
