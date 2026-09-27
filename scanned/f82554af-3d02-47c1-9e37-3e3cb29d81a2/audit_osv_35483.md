# [M] Gnutls: stack-based buffer overflow in gnutls_pkcs11_token_init() function

## Summary
Severity: Medium
Advisory: CVE-2025-9820
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2025-9820
Type: osv

## Details
A flaw was found in the GnuTLS library, specifically in the gnutls_pkcs11_token_init() function that handles PKCS#11 token initialization. When a token label longer than expected is processed, the function writes past the end of a fixed-size stack buffer. This programming error can cause the application using GnuTLS to crash or, in certain conditions, be exploited for code execution. As a result, systems or applications relying on GnuTLS may be vulnerable to a denial of service or local privilege escalation attacks.

## References
- http://www.openwall.com/lists/oss-security/2025/11/20/2
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://www.gnutls.org/security-new.html#GNUTLS-SA-2025-11-18
- https://access.redhat.com/errata/RHSA-2026:13812
- https://access.redhat.com/errata/RHSA-2026:3477
- https://access.redhat.com/errata/RHSA-2026:4188
- https://access.redhat.com/errata/RHSA-2026:4655
- https://access.redhat.com/errata/RHSA-2026:4943
- https://access.redhat.com/errata/RHSA-2026:5585
- https://access.redhat.com/errata/RHSA-2026:5606
- https://access.redhat.com/errata/RHSA-2026:7329
- https://access.redhat.com/errata/RHSA-2026:7477
- https://access.redhat.com/security/cve/CVE-2025-9820
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9820.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9820
- https://bugzilla.redhat.com/show_bug.cgi?id=2392528
- https://gitlab.com/gnutls/gnutls/-/issues/1732
- https://gitlab.com/gnutls/gnutls/-/commit/1d56f96f6ab5034d677136b9d50b5a75dff0faf5
