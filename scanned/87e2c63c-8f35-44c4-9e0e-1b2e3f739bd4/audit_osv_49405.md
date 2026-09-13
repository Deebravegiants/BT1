# [M] CVE-2019-11727

## Summary
Severity: Medium
Advisory: CVE-2019-11727
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11727
Type: osv

## Details
A vulnerability exists where it possible to force Network Security Services (NSS) to sign CertificateVerify with PKCS#1 v1.5 signatures when those are the only ones advertised by server in CertificateRequest in TLS 1.3. PKCS#1 v1.5 signatures should not be used for TLS 1.3 messages. This vulnerability affects Firefox < 68.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00011.html
- https://access.redhat.com/errata/RHSA-2019:1951
- https://security.gentoo.org/glsa/201908-12
- https://www.mozilla.org/security/advisories/mfsa2019-21/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1552208
