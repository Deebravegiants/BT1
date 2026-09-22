# [M] CVE-2025-32989

## Summary
Severity: Medium
Advisory: CVE-2025-32989
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-32989
Type: osv

## Details
A heap-buffer-overread vulnerability was found in GnuTLS in how it handles the Certificate Transparency (CT) Signed Certificate Timestamp (SCT) extension during X.509 certificate parsing. This flaw allows a malicious user to create a certificate containing a malformed SCT extension (OID 1.3.6.1.4.1.11129.2.4.2) that contains sensitive data. This issue leads to the exposure of confidential information when GnuTLS verifies certificates from certain websites when the certificate (SCT) is not checked correctly.

## References
- http://www.openwall.com/lists/oss-security/2025/07/11/3
- https://access.redhat.com/errata/RHSA-2025:17361
- https://access.redhat.com/errata/RHSA-2025:19088
- https://access.redhat.com/security/cve/CVE-2025-32989
- https://access.redhat.com/errata/RHSA-2025:17181
- https://access.redhat.com/errata/RHSA-2025:17348
- https://access.redhat.com/errata/RHSA-2025:22529
- https://access.redhat.com/errata/RHSA-2025:16115
- https://access.redhat.com/errata/RHSA-2025:16116
- https://bugzilla.redhat.com/show_bug.cgi?id=2359621
