# [H] CVE-2023-0361

## Summary
Severity: High
Advisory: CVE-2023-0361
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-15
Source: https://osv.dev/vulnerability/CVE-2023-0361
Type: osv

## Details
A timing side-channel in the handling of RSA ClientKeyExchange messages was discovered in GnuTLS. This side-channel can be sufficient to recover the key encrypted in the RSA ciphertext across a network in a Bleichenbacher style attack. To achieve a successful decryption the attacker would need to send a large amount of specially crafted messages to the vulnerable server. By recovering the secret from the ClientKeyExchange message, the attacker would be able to decrypt the application data exchanged over that connection.

## References
- https://access.redhat.com/security/cve/CVE-2023-0361
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0361.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UFIA3X4IZ3CW7SRQ2UHNHNPMRIAWF2FI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WS4KVDOG6QTALWHC2QE4Y7VPDRMLTRWQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z634YBXAJ5VLDI62IOPBVP5K6YFHAWCY/
- https://nvd.nist.gov/vuln/detail/CVE-2023-0361
- https://security.netapp.com/advisory/ntap-20230324-0005/
- https://security.netapp.com/advisory/ntap-20230725-0005/
- https://gitlab.com/gnutls/gnutls/-/issues/1050
- https://github.com/tlsfuzzer/tlsfuzzer/pull/679
- https://lists.debian.org/debian-lts-announce/2023/02/msg00015.html
