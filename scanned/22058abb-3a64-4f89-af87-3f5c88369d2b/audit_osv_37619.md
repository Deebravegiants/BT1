# [H] OCSP designated-responder authorization bypass via missing signature verification

## Summary
Severity: High
Advisory: CVE-2026-32144
Aliases: EEF-CVE-2026-32144, GHSA-gxrm-pf64-99xm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-32144
Type: osv

## Details
Improper Certificate Validation vulnerability in Erlang OTP public_key (pubkey_ocsp module) allows OCSP designated-responder authorization bypass via missing signature verification.

The OCSP response validation in public_key:pkix_ocsp_validate/5 does not verify that a CA-designated responder certificate was cryptographically signed by the issuing CA. Instead, it only checks that the responder certificate's issuer name matches the CA's subject name and that the certificate has the OCSPSigning extended key usage. An attacker who can intercept or control OCSP responses can create a self-signed certificate with a matching issuer name and the OCSPSigning EKU, and use it to forge OCSP responses that mark revoked certificates as valid.

This affects SSL/TLS clients using OCSP stapling, which may accept connections to servers with revoked certificates, potentially transmitting sensitive data to compromised servers. Applications using the public_key:pkix_ocsp_validate/5 API directly are also affected, with impact depending on usage context.

This vulnerability is associated with program files lib/public_key/src/pubkey_ocsp.erl and program routines pubkey_ocsp:is_authorized_responder/3.

This issue affects OTP from OTP 27.0 before OTP 28.4.2 and OTP 27.3.4.10, corresponding to public_key from 1.16 before 1.20.3 and 1.17.1.2, and ssl from 11.2 before 11.5.4 and 11.2.12.7.

## References
- https://cna.erlef.org/cves/CVE-2026-32144.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-32144
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32144.json
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://access.redhat.com/security/cve/CVE-2026-32144
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32144.json
- https://github.com/erlang/otp/security/advisories/GHSA-gxrm-pf64-99xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32144
- https://bugzilla.redhat.com/show_bug.cgi?id=2455896
- https://github.com/erlang/otp/commit/49033a6d93a5be0ee0dce04e1fb8b4ae7de1e0c0
- https://github.com/erlang/otp/commit/ac7ff528be857c5d35eb29c7f24106e3a16d4891
- https://github.com/erlang/otp
