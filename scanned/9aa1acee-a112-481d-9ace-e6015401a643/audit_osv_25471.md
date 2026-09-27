# [C] TLS 1.3 client issue handling malicious server when not including a KSE and PSK extension

## Summary
Severity: Critical
Advisory: CVE-2023-3724
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-07-17
Source: https://osv.dev/vulnerability/CVE-2023-3724
Type: osv

## Details
If a TLS 1.3 client gets neither a PSK (pre shared key) extension nor a KSE (key share extension) when connecting to a malicious server, a default predictable buffer gets used for the IKM (Input Keying Material) value when generating the session master secret. Using a potentially known IKM value when generating the session master secret key compromises the key generated, allowing an eavesdropper to reconstruct it and potentially allowing access to or meddling with message contents in the session. This issue does not affect client validation of connected servers, nor expose private key information, but could result in an insecure TLS 1.3 session when not controlling both sides of the connection. wolfSSL recommends that TLS 1.3 client side users update the version of wolfSSL used.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3724.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3724
- https://github.com/wolfSSL/wolfssl/pull/6412
