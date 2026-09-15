# [M] CVE-2026-50721

## Summary
Severity: Medium
Advisory: CVE-2026-50721
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-50721
Type: osv

## Details
Libreswan, via the function RSA_authenticate_hash_signature_raw_rsa(), did not correctly verify the length of the authentication hash when the SIG payload of an IKEv1 packet was encoded using PKCS #1 RSA Encryption as per RFC 2313. A remote attacker can use a variation on the Bleichenbacher attack to forge the SIG payload when small public exponents are being used (e.g., e=3), which could lead to impersonation. Additionally, a remote attacker, by encoding a shorter than expected hash in the SIG payload, could trigger an assertion leading to denial-of-service. The daemon aborts and restarts; continued exploitation causes sustained denial of service. Remote code execution is not possible. X.509 certificate verifications of remote IKE peers are not affected.

## References
- https://libreswan.org/security/CVE-2026-50721/
- https://libreswan.org/security/CVE-2026-50721/CVE-2026-50721.txt
- https://libreswan.org/security/CVE-2026-50722/CVE-2026-50722.txt
- https://www.rfc-editor.org/rfc/rfc2313
