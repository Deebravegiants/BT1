# [M] Gnutls: timing side-channel in the rsa-psk authentication

## Summary
Severity: Medium
Advisory: CVE-2023-5981
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-11-28
Source: https://osv.dev/vulnerability/CVE-2023-5981
Type: osv

## Details
A vulnerability was found that the response times to malformed ciphertexts in RSA-PSK ClientKeyExchange differ from response times of ciphertexts with correct PKCS#1 v1.5 padding.

## References
- http://www.openwall.com/lists/oss-security/2024/01/19/3
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://gnutls.org/security-new.html#GNUTLS-SA-2023-10-23
- https://lists.debian.org/debian-lts-announce/2023/11/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7ZEIOLORQ7N6WRPFXZSYDL2MC4LP7VFV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GNXKVR5YNUEBNHAHM5GSYKBZX4W2HMN2/
- https://access.redhat.com/errata/RHSA-2024:0155
- https://access.redhat.com/errata/RHSA-2024:0319
- https://access.redhat.com/errata/RHSA-2024:0399
- https://access.redhat.com/errata/RHSA-2024:0451
- https://access.redhat.com/errata/RHSA-2024:0533
- https://access.redhat.com/errata/RHSA-2024:1383
- https://access.redhat.com/errata/RHSA-2024:2094
- https://access.redhat.com/security/cve/CVE-2023-5981
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5981.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5981
- https://bugzilla.redhat.com/show_bug.cgi?id=2248445
