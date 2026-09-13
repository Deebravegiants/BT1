# [M] CVE-2022-48437

## Summary
Severity: Medium
Advisory: CVE-2022-48437
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2022-48437
Type: osv

## Details
An issue was discovered in x509/x509_verify.c in LibreSSL before 3.6.1, and in OpenBSD before 7.2 errata 001. x509_verify_ctx_add_chain does not store errors that occur during leaf certificate verification, and therefore an incorrect error is returned. This behavior occurs when there is an installed verification callback that instructs the verifier to continue upon detecting an invalid certificate.

## References
- https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-3.6.1-relnotes.txt
- https://ftp.openbsd.org/pub/OpenBSD/patches/7.2/common/001_x509.patch.sig
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48437.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48437
- https://github.com/openbsd/src/commit/4f94258c65a918ee3d8670e93916d15bf879e6ec
