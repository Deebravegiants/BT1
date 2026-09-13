# [M] Gnutls: potential crash during chain building/verification

## Summary
Severity: Medium
Advisory: CVE-2024-28835
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-28835
Type: osv

## Details
A flaw has been discovered in GnuTLS where an application crash can be induced when attempting to verify a specially crafted .pem bundle using the "certtool --verify-chain" command.

## References
- http://www.openwall.com/lists/oss-security/2024/03/22/1
- http://www.openwall.com/lists/oss-security/2024/03/22/2
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/09/msg00019.html
- https://lists.gnupg.org/pipermail/gnutls-help/2024-March/004845.html
- https://access.redhat.com/errata/RHSA-2024:1879
- https://access.redhat.com/errata/RHSA-2024:2570
- https://access.redhat.com/errata/RHSA-2024:2889
- https://access.redhat.com/security/cve/CVE-2024-28835
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28835.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28835
- https://security.netapp.com/advisory/ntap-20241122-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=2269084
- https://gitlab.com/gnutls/gnutls/
