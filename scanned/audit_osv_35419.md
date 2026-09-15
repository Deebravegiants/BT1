# [M] Curve25519 Blinding

## Summary
Severity: Medium
Advisory: CVE-2025-7396
CVSS: 6.0 (CVSS:4.0/AV:P/AC:H/AT:P/PR:L/UI:A/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-7396
Type: osv

## Details
In wolfSSL release 5.8.2 blinding support is turned on by default for Curve25519 in applicable builds. The blinding configure option is only for the base C implementation of Curve25519. It is not needed, or available with; ARM assembly builds, Intel assembly builds, and the small Curve25519 feature. While the side-channel attack on extracting a private key would be very difficult to execute in practice, enabling blinding provides an additional layer of protection for devices that may be more susceptible to physical access or side-channel observation.

## References
- https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md#wolfssl-release-582-july-17-2025
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7396.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7396
- https://github.com/wolfssl/wolfssl
