# [M] OCSP CertID serial-number length-confusion in `wolfSSL_OCSP_resp_find_status` allows a same-issuer...

## Summary
Severity: Medium
Advisory: JLSEC-2026-694
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-694
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
OCSP CertID serial-number length-confusion in `wolfSSL_OCSP_resp_find_status` allows a same-issuer SingleResponse whose serial is a prefix of the target serial to be reported as the revocation status of a different certificate. The lookup compared serial-number bytes without first requiring the two serial numbers to be of equal length, so a SingleResponse for one certificate (same issuer) whose serial is a prefix of the target's serial would match, returning the wrong certificate's status. The fix requires the serial lengths to be equal before comparing the serial bytes.

## References
- https://github.com/advisories/GHSA-xpv9-p7vg-qhrc
- https://github.com/wolfSSL/wolfssl/pull/10554
- https://nvd.nist.gov/vuln/detail/CVE-2026-10098
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
