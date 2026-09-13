# [M] Silent Drop of TLS 1.3 Encrypted Records in s2n-tls

## Summary
Severity: Medium
Advisory: CVE-2026-16317
Aliases: GHSA-684c-v35q-fvx7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:L/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-16317
Type: osv

## Details
Missing validation of the outer content_type byte on TLS 1.3 encrypted records in s2n-tls allows an active man-in-the-middle to silently discard individual application data records without either endpoint detecting the modification. RFC 8446 Section 5.2 requires that the outer content_type of all encrypted TLS 1.3 records must be application_data (0x17). The s2n-tls AEAD implementation hardcodes this value in the additional authenticated data rather than using the actual wire byte, so the outer content_type is not covered by the authentication tag. 



This enables selective suppression of application data. In HTTP pipelining scenarios, dropping a TLS record containing an HTTP request can cause request/response desynchronization, where subsequent responses are delivered to the wrong requests. In write-heavy workloads, a dropped record containing a write request can result in undetectable data loss when the client interprets a subsequent success response as confirmation of the dropped write.



All TLS 1.3 connections are affected. Both TLS clients and servers are affected. TLS 1.2 and QUIC connections are not affected.



We recommend you upgrade s2n-tls to version v1.7.6

## References
- https://aws.amazon.com/security/security-bulletins/2026-062-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16317.json
- https://github.com/aws/s2n-tls/security/advisories/GHSA-684c-v35q-fvx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-16317
- https://github.com/aws/s2n-tls/releases/tag/v1.7.6
