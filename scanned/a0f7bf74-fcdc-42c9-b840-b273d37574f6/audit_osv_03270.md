# [M] ALPINE-CVE-2025-32989

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-32989
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-32989
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.11-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.11-r0

## Details
A heap-buffer-overread vulnerability was found in GnuTLS in how it handles the Certificate Transparency (CT) Signed Certificate Timestamp (SCT) extension during X.509 certificate parsing. This flaw allows a malicious user to create a certificate containing a malformed SCT extension (OID 1.3.6.1.4.1.11129.2.4.2) that contains sensitive data. This issue leads to the exposure of confidential information when GnuTLS verifies certificates from certain websites when the certificate (SCT) is not checked correctly.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-32989
