# [H] JLSEC-2026-526

## Summary
Severity: High
Advisory: JLSEC-2026-526
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-526
Type: osv

## Affected
- Julia: `GnuTLS_jll` — affected >=3.7.1+0 <3.8.3+0

## Details
A vulnerability was found in GnuTLS, where a cockpit (which uses gnuTLS) rejects a certificate chain with distributed trust. This issue occurs when validating a certificate chain with cockpit-certificate-ensure. This flaw allows an unauthenticated, remote client or attacker to initiate a denial of service attack.

## References
- http://www.openwall.com/lists/oss-security/2024/01/19/3
- https://access.redhat.com/errata/RHSA-2024:0533
- https://access.redhat.com/errata/RHSA-2024:1082
- https://access.redhat.com/errata/RHSA-2024:1383
- https://access.redhat.com/errata/RHSA-2024:2094
- https://access.redhat.com/security/cve/CVE-2024-0567
- https://bugzilla.redhat.com/show_bug.cgi?id=2258544
- https://gitlab.com/gnutls/gnutls/-/issues/1521
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7ZEIOLORQ7N6WRPFXZSYDL2MC4LP7VFV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GNXKVR5YNUEBNHAHM5GSYKBZX4W2HMN2/
- https://lists.gnupg.org/pipermail/gnutls-help/2024-January/004841.html
- https://security.netapp.com/advisory/ntap-20240202-0011/
