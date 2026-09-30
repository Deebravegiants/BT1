# [M] Opencryptoki: timing side-channel in handling of rsa pkcs#1 v1.5 padded ciphertexts (marvin)

## Summary
Severity: Medium
Advisory: CVE-2024-0914
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-31
Source: https://osv.dev/vulnerability/CVE-2024-0914
Type: osv

## Details
A timing side-channel vulnerability has been discovered in the opencryptoki package while processing RSA PKCS#1 v1.5 padded ciphertexts. This flaw could potentially enable unauthorized RSA ciphertext decryption or signing, even without access to the corresponding private key.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://people.redhat.com/~hkario/marvin/
- https://access.redhat.com/errata/RHSA-2024:1239
- https://access.redhat.com/errata/RHSA-2024:1411
- https://access.redhat.com/errata/RHSA-2024:1608
- https://access.redhat.com/errata/RHSA-2024:1856
- https://access.redhat.com/errata/RHSA-2024:1992
- https://access.redhat.com/security/cve/CVE-2024-0914
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0914.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0914
- https://bugzilla.redhat.com/show_bug.cgi?id=2260407
- https://github.com/opencryptoki/opencryptoki
