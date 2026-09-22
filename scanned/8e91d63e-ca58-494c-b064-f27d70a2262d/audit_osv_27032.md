# [H] Gnutls: incomplete fix for cve-2023-5981

## Summary
Severity: High
Advisory: CVE-2024-0553
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/CVE-2024-0553
Type: osv

## Details
A vulnerability was found in GnuTLS. The response times to malformed ciphertexts in RSA-PSK ClientKeyExchange differ from the response times of ciphertexts with correct PKCS#1 v1.5 padding. This issue may allow a remote attacker to perform a timing side-channel attack in the RSA-PSK key exchange, potentially leading to the leakage of sensitive data. CVE-2024-0553 is designated as an incomplete resolution for CVE-2023-5981.

## References
- http://www.openwall.com/lists/oss-security/2024/01/19/3
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://gnutls.org/download.html
- https://lists.debian.org/debian-lts-announce/2024/02/msg00010.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7ZEIOLORQ7N6WRPFXZSYDL2MC4LP7VFV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GNXKVR5YNUEBNHAHM5GSYKBZX4W2HMN2/
- https://lists.gnupg.org/pipermail/gnutls-help/2024-January/004841.html
- https://access.redhat.com/errata/RHSA-2024:0533
- https://access.redhat.com/errata/RHSA-2024:0627
- https://access.redhat.com/errata/RHSA-2024:0796
- https://access.redhat.com/errata/RHSA-2024:1082
- https://access.redhat.com/errata/RHSA-2024:1108
- https://access.redhat.com/errata/RHSA-2024:1383
- https://access.redhat.com/errata/RHSA-2024:2094
- https://access.redhat.com/security/cve/CVE-2024-0553
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0553.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0553
- https://security.netapp.com/advisory/ntap-20240202-0011/
- https://bugzilla.redhat.com/show_bug.cgi?id=2258412
